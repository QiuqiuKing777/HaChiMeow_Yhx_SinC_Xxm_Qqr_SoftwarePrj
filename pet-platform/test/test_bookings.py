"""TC-013 提交服务预约 / TC-014 预约时段已满 / TC-015 发布方确认预约"""

import pytest
from app.models import Booking, ServiceSlot


class TestSubmitBooking:
    """TC-013: 提交服务预约"""

    def test_submit_booking_success(self, client, normal_user_auth, test_service):
        slot = test_service._test_slot
        resp = client.post('/api/bookings', json={
            'slot_id': slot.slot_id,
            'pet_name': '小花',
            'pet_breed': '英短',
            'remark': '比较乖',
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        data = resp.get_json()
        assert '预约成功' in data['message']
        booking = data['booking']
        assert booking['booking_status'] == 'pending'

    def test_submit_booking_increments_booked_count(self, client, normal_user_auth, test_service, app):
        from app.extensions import db

        slot = test_service._test_slot
        before = slot.booked_count

        client.post('/api/bookings', json={
            'slot_id': slot.slot_id,
            'pet_name': '小白',
        }, headers=normal_user_auth)

        with app.app_context():
            updated_slot = db.session.get(ServiceSlot, slot.slot_id)
            assert updated_slot.booked_count == before + 1


class TestBookingSlotFull:
    """TC-014: 预约时段已满"""

    def test_booking_slot_full(self, client, normal_user_auth, test_slot_full):
        slot = test_slot_full._test_slot
        assert slot.booked_count >= slot.capacity

        resp = client.post('/api/bookings', json={
            'slot_id': slot.slot_id,
            'pet_name': '小黑',
        }, headers=normal_user_auth)
        assert resp.status_code == 400
        data = resp.get_json()
        assert '已约满' in data['error']


class TestConfirmBooking:
    """TC-015: 发布方确认预约"""

    @pytest.fixture
    def pending_booking(self, app, test_service, normal_user):
        from app.extensions import db

        slot = test_service._test_slot
        booking = Booking(
            service_id=test_service.service_id,
            user_id=normal_user.user_id,
            slot_id=slot.slot_id,
            pet_name='旺财',
            booking_status='pending',
        )
        db.session.add(booking)
        db.session.commit()
        return booking

    def test_confirm_booking(self, client, publisher_user_auth, pending_booking):
        resp = client.put(
            f'/api/bookings/{pending_booking.booking_id}/confirm',
            headers=publisher_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '预约已确认'
        assert data['booking']['booking_status'] == 'confirmed'

    def test_confirm_booking_unauthorized(self, client, normal_user_auth, pending_booking):
        resp = client.put(
            f'/api/bookings/{pending_booking.booking_id}/confirm',
            headers=normal_user_auth,
        )
        assert resp.status_code == 403

    def test_confirm_booking_already_confirmed(self, client, publisher_user_auth, pending_booking):
        client.put(
            f'/api/bookings/{pending_booking.booking_id}/confirm',
            headers=publisher_user_auth,
        )
        resp = client.put(
            f'/api/bookings/{pending_booking.booking_id}/confirm',
            headers=publisher_user_auth,
        )
        assert resp.status_code == 400


class TestBookingCancel:
    """预约取消"""

    @pytest.fixture
    def pending_booking(self, app, test_service, normal_user):
        from app.extensions import db

        slot = test_service._test_slot
        booking = Booking(
            service_id=test_service.service_id,
            user_id=normal_user.user_id,
            slot_id=slot.slot_id,
            pet_name='旺财',
            booking_status='pending',
        )
        db.session.add(booking)
        db.session.commit()
        return booking

    def test_cancel_booking(self, client, normal_user_auth, pending_booking):
        resp = client.put(
            f'/api/bookings/{pending_booking.booking_id}/cancel',
            headers=normal_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['booking']['booking_status'] == 'cancelled'

    def test_cancel_booking_restores_slot_capacity(self, client, normal_user_auth, pending_booking, app):
        from app.extensions import db
        from app.models import ServiceSlot

        slot = pending_booking.slot
        slot.booked_count = 1
        db.session.commit()
        before = slot.booked_count

        client.put(
            f'/api/bookings/{pending_booking.booking_id}/cancel',
            headers=normal_user_auth,
        )

        with app.app_context():
            updated_slot = db.session.get(ServiceSlot, slot.slot_id)
            assert updated_slot.booked_count == before - 1


class TestServiceSlots:
    """查询服务可用时段"""

    def test_get_service_slots(self, client, test_service):
        resp = client.get(f'/api/services/{test_service.service_id}/slots')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        slot = data[0]
        assert 'slot_date' in slot
        assert 'available' in slot
