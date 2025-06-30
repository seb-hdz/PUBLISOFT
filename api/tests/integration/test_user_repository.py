import pytest
from sqlalchemy.orm import Session
from modules.auth.infrastructure.database.repositories.user_repository import (
    UserRepositorySQLAlchemy,
)
from modules.auth.infrastructure.database.models.users import User as UserModel
from modules.auth.domain.entities.user import User, UserStateEnum, UserRoleEnum
from modules.auth.domain.value_objects.vo import EmailVO, UserCodeVO, PasswordHashVO
from datetime import datetime, timezone


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.auth
class TestUserRepository:
    """Integration tests for UserRepository with database."""

    @pytest.mark.integration
    @pytest.mark.database
    def test_add_user(self, db_session):
        """Test adding a user to the database."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create a domain user
        email = EmailVO("test@example.com")
        password_hash = PasswordHashVO("hashed_password_123")
        user_code = UserCodeVO("USER123")

        user = User.create(
            email=email,
            hash_password=password_hash,
            user_code=user_code,
            name="Test",
            last_name="User",
        )

        # Act
        repository.add(user)
        db_session.commit()

        # Assert
        db_user = (
            db_session.query(UserModel).filter_by(email="test@example.com").first()
        )
        assert db_user is not None
        assert db_user.email == "test@example.com"
        assert db_user.user_code == "USER123"
        assert db_user.role == "STUDENT"
        assert db_user.state == "ACTIVE"

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_by_email_existing_user(self, db_session):
        """Test getting a user by email when user exists."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add a user to database
        db_user = UserModel(
            id="test-id-123",
            email="test@example.com",
            hash_password="hashed_password_123",
            user_code="USER123",
            name="Test",
            last_name="User",
            role="STUDENT",
            state="ACTIVE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(db_user)
        db_session.commit()

        # Act
        result = repository.get_by_email("test@example.com")

        # Assert
        assert result is not None
        assert result.email.email == "test@example.com"
        assert result.user_code.user_code == "USER123"
        assert result.role == UserRoleEnum.STUDENT
        assert result.state == UserStateEnum.ACTIVE

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_by_email_nonexistent_user(self, db_session):
        """Test getting a user by email when user doesn't exist."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Act
        result = repository.get_by_email("nonexistent@example.com")

        # Assert
        assert result is None

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_by_id_existing_user(self, db_session):
        """Test getting a user by ID when user exists."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)
        user_id = "test-id-123"

        # Create and add a user to database
        db_user = UserModel(
            id=user_id,
            email="test@example.com",
            hash_password="hashed_password_123",
            user_code="USER123",
            name="Test",
            last_name="User",
            role="STUDENT",
            state="ACTIVE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(db_user)
        db_session.commit()

        # Act
        result = repository.get_by_id(user_id)

        # Assert
        assert result is not None
        assert result.id == user_id
        assert result.email.email == "test@example.com"

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_by_id_nonexistent_user(self, db_session):
        """Test getting a user by ID when user doesn't exist."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Act
        result = repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    @pytest.mark.integration
    @pytest.mark.database
    def test_update_user(self, db_session):
        """Test updating a user in the database."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add a user to database
        db_user = UserModel(
            id="test-id-123",
            email="test@example.com",
            hash_password="hashed_password_123",
            user_code="USER123",
            name="Test",
            last_name="User",
            role="STUDENT",
            state="ACTIVE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(db_user)
        db_session.commit()

        # Get the domain user
        user = repository.get_by_id("test-id-123")

        # Update the user
        user.state = UserStateEnum.SUSPENDED
        user.role = UserRoleEnum.ADMIN

        # Act
        repository.update(user)
        db_session.commit()

        # Assert
        updated_db_user = (
            db_session.query(UserModel).filter_by(id="test-id-123").first()
        )
        assert updated_db_user.state == "SUSPENDED"
        assert updated_db_user.role == "ADMIN"

    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_user(self, db_session):
        """Test deleting a user from the database."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add a user to database
        db_user = UserModel(
            id="test-id-123",
            email="test@example.com",
            hash_password="hashed_password_123",
            user_code="USER123",
            name="Test",
            last_name="User",
            role="STUDENT",
            state="ACTIVE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(db_user)
        db_session.commit()

        # Get the domain user
        user = repository.get_by_id("test-id-123")

        # Act
        repository.delete(user)
        db_session.commit()

        # Assert
        deleted_user = db_session.query(UserModel).filter_by(id="test-id-123").first()
        assert deleted_user is None

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_all_users(self, db_session):
        """Test getting all users from the database."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add multiple users to database
        users_data = [
            {
                "id": "test-id-1",
                "email": "user1@example.com",
                "hash_password": "hashed_password_1",
                "user_code": "USER001",
                "name": "User1",
                "last_name": "Test",
                "role": "STUDENT",
                "state": "ACTIVE",
            },
            {
                "id": "test-id-2",
                "email": "user2@example.com",
                "hash_password": "hashed_password_2",
                "user_code": "USER002",
                "name": "User2",
                "last_name": "Test",
                "role": "ADMIN",
                "state": "ACTIVE",
            },
        ]

        for user_data in users_data:
            db_user = UserModel(
                **user_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(db_user)

        db_session.commit()

        # Act
        result = repository.get_all()

        # Assert
        assert len(result) == 2
        emails = [user.email.email for user in result]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_users_by_role(self, db_session):
        """Test getting users by role."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add users with different roles
        users_data = [
            {
                "id": "test-id-1",
                "email": "student@example.com",
                "hash_password": "hashed_password_1",
                "user_code": "USER001",
                "name": "Student",
                "last_name": "Test",
                "role": "STUDENT",
                "state": "ACTIVE",
            },
            {
                "id": "test-id-2",
                "email": "admin@example.com",
                "hash_password": "hashed_password_2",
                "user_code": "USER002",
                "name": "Admin",
                "last_name": "Test",
                "role": "ADMIN",
                "state": "ACTIVE",
            },
            {
                "id": "test-id-3",
                "email": "student2@example.com",
                "hash_password": "hashed_password_3",
                "user_code": "USER003",
                "name": "Student2",
                "last_name": "Test",
                "role": "STUDENT",
                "state": "ACTIVE",
            },
        ]

        for user_data in users_data:
            db_user = UserModel(
                **user_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(db_user)

        db_session.commit()

        # Act
        students = repository.get_by_role(UserRoleEnum.STUDENT)
        admins = repository.get_by_role(UserRoleEnum.ADMIN)

        # Assert
        assert len(students) == 2
        assert len(admins) == 1

        student_emails = [user.email.email for user in students]
        assert "student@example.com" in student_emails
        assert "student2@example.com" in student_emails

        admin_emails = [user.email.email for user in admins]
        assert "admin@example.com" in admin_emails

    @pytest.mark.integration
    @pytest.mark.database
    def test_get_users_by_state(self, db_session):
        """Test getting users by state."""
        # Arrange
        repository = UserRepositorySQLAlchemy(db_session)

        # Create and add users with different states
        users_data = [
            {
                "id": "test-id-1",
                "email": "active@example.com",
                "hash_password": "hashed_password_1",
                "user_code": "USER001",
                "name": "Active",
                "last_name": "User",
                "role": "STUDENT",
                "state": "ACTIVE",
            },
            {
                "id": "test-id-2",
                "email": "suspended@example.com",
                "hash_password": "hashed_password_2",
                "user_code": "USER002",
                "name": "Suspended",
                "last_name": "User",
                "role": "STUDENT",
                "state": "SUSPENDED",
            },
            {
                "id": "test-id-3",
                "email": "active2@example.com",
                "hash_password": "hashed_password_3",
                "user_code": "USER003",
                "name": "Active2",
                "last_name": "User",
                "role": "STUDENT",
                "state": "ACTIVE",
            },
        ]

        for user_data in users_data:
            db_user = UserModel(
                **user_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db_session.add(db_user)

        db_session.commit()

        # Act
        active_users = repository.get_by_state(UserStateEnum.ACTIVE)
        suspended_users = repository.get_by_state(UserStateEnum.SUSPENDED)

        # Assert
        assert len(active_users) == 2
        assert len(suspended_users) == 1

        active_emails = [user.email.email for user in active_users]
        assert "active@example.com" in active_emails
        assert "active2@example.com" in active_emails

        suspended_emails = [user.email.email for user in suspended_users]
        assert "suspended@example.com" in suspended_emails
