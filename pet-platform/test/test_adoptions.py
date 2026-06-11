"""TC-006 提交领养申请 / TC-007 重复提交领养申请 / TC-008 发布方审核通过申请"""

import pytest
from app.models import AdoptionApplication


class TestSubmitAdoption:
    """TC-006: 提交领养申请"""

    def test_submit_adoption_success(self, client, normal_user_auth, test_pet):
        resp = client.post('/api/adoptions', json={
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房，120平米，环境宽敞',
            'pet_experience': '曾养过一只狗，有5年饲养经验',
            'family_attitude': '全家都支持领养',
            'promise_statement': '我承诺不会遗弃宠物，会定期打疫苗、驱虫',
            'contact_info': '手机号138xxxx，微信号123456',
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        data = resp.get_json()
        assert '申请提交成功' in data['message']
        app_data = data['application']
        assert app_data['review_status'] == 'pending'

    def test_submit_adoption_pet_not_online(self, client, normal_user_auth, app, publisher_user):
        from app.extensions import db
        from app.models import Pet

        pet = Pet(
            publisher_id=publisher_user.user_id,
            pet_name='小黑',
            species='犬',
            breed='拉布拉多',
            status='adopted',
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post('/api/adoptions', json={
            'pet_id': pet.pet_id,
            'housing_info': '自有住房',
            'promise_statement': '我承诺善待宠物',
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_submit_adoption_missing_required(self, client, normal_user_auth, test_pet):
        """缺少必填字段"""
        resp = client.post('/api/adoptions', json={
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房',
        }, headers=normal_user_auth)
        assert resp.status_code == 400


class TestDuplicateAdoption:
    """TC-007: 重复提交领养申请"""

    def test_duplicate_adoption_rejected(self, client, normal_user_auth, test_pet):
        payload = {
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房',
            'pet_experience': '有经验',
            'family_attitude': '支持',
            'promise_statement': '承诺善待宠物',
            'contact_info': '手机138xxxx',
        }
        # 首次提交
        r1 = client.post('/api/adoptions', json=payload, headers=normal_user_auth)
        assert r1.status_code == 201

        # 重复提交
        r2 = client.post('/api/adoptions', json=payload, headers=normal_user_auth)
        assert r2.status_code == 409
        data = r2.get_json()
        assert '已提交' in data['error']

    def test_duplicate_adoption_by_status_pending(self, client, normal_user_auth, test_pet, app):
        """已有 pending 申请时不可重复提交"""
        from app.extensions import db

        existing = AdoptionApplication(
            pet_id=test_pet.pet_id,
            applicant_id=1,
            housing_info='自有住房',
            promise_statement='承诺',
            review_status='pending',
        )
        db.session.add(existing)
        db.session.commit()

        resp = client.post('/api/adoptions', json={
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房',
            'promise_statement': '我承诺善待宠物',
        }, headers=normal_user_auth)
        assert resp.status_code == 409


class TestReviewAdoption:
    """TC-008: 发布方审核通过申请"""

    @pytest.fixture
    def pending_application(self, app, test_pet, normal_user):
        from app.extensions import db

        app_obj = AdoptionApplication(
            pet_id=test_pet.pet_id,
            applicant_id=normal_user.user_id,
            housing_info='自有住房',
            pet_experience='有经验',
            family_attitude='支持',
            promise_statement='承诺',
            review_status='pending',
        )
        db.session.add(app_obj)
        db.session.commit()
        return app_obj

    def test_review_approve(self, client, publisher_user_auth, pending_application):
        resp = client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'approved', 'review_remark': '同意领养'},
            headers=publisher_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '审核完成'
        assert data['application']['review_status'] == 'approved'

    def test_review_reject(self, client, publisher_user_auth, pending_application):
        resp = client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'rejected', 'review_remark': '条件不符合'},
            headers=publisher_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['application']['review_status'] == 'rejected'

    def test_review_auto_reject_other_pending(self, client, publisher_user_auth, pending_application, test_pet, app):
        """审核通过后，同宠物其他待审核申请自动拒绝"""
        from app.extensions import db

        other = AdoptionApplication(
            pet_id=test_pet.pet_id,
            applicant_id=2,
            housing_info='租房',
            promise_statement='承诺',
            review_status='pending',
        )
        db.session.add(other)
        db.session.commit()

        client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'approved'},
            headers=publisher_user_auth,
        )

        from app.extensions import db
        other_updated = db.session.get(AdoptionApplication, other.application_id)
        assert other_updated.review_status == 'rejected'

    def test_review_unauthorized(self, client, normal_user_auth, pending_application):
        """普通用户无权审核"""
        resp = client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'approved'},
            headers=normal_user_auth,
        )
        assert resp.status_code == 403

    def test_review_already_reviewed(self, client, publisher_user_auth, pending_application):
        """已完成审核的申请不能重复审核"""
        client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'approved'},
            headers=publisher_user_auth,
        )
        resp = client.put(
            f'/api/adoptions/{pending_application.application_id}/review',
            json={'review_status': 'rejected'},
            headers=publisher_user_auth,
        )
        assert resp.status_code == 400


class TestMyApplications:
    """查询我的申请列表"""

    def test_my_applications(self, client, normal_user_auth):
        resp = client.get('/api/adoptions/my', headers=normal_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data

    def test_my_applications_filter_status(self, client, normal_user_auth):
        resp = client.get('/api/adoptions/my?status=pending', headers=normal_user_auth)
        assert resp.status_code == 200
