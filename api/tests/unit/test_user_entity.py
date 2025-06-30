import pytest
from datetime import datetime, timezone
from modules.auth.domain.entities.user import User, UserStateEnum, UserRoleEnum
from modules.auth.domain.value_objects.vo import EmailVO, UserCodeVO, PasswordHashVO
from modules.auth.domain.events.user_events import UserCreatedEvent


@pytest.mark.unit
@pytest.mark.auth
class TestUserEntity:
    """Test cases for the User domain entity."""

    @pytest.mark.unit
    def test_user_creation_with_valid_data(self):
        """Test creating a user with valid data."""
        # Arrange
        email = EmailVO("test@example.com")
        password_hash = PasswordHashVO("hashed_password_123")
        user_code = UserCodeVO("USER123")

        # Act
        user = User.create(
            email=email,
            hash_password=password_hash,
            user_code=user_code,
            name="Test",
            last_name="User",
        )

        # Assert
        assert user.email == email
        assert user.hash_password == password_hash
        assert user.user_code == user_code
        assert user.state == UserStateEnum.ACTIVE
        assert user.role == UserRoleEnum.STUDENT
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

        # Check that UserCreatedEvent was added to events
        events = list(user.events)
        assert len(events) == 1
        assert isinstance(events[0], UserCreatedEvent)
        assert events[0].user_id == user.id
        assert events[0].email == "test@example.com"
        assert events[0].user_code == "USER123"

    @pytest.mark.unit
    def test_user_creation_with_admin_role(self):
        """Test creating a user with admin role."""
        # Arrange
        email = EmailVO("admin@example.com")
        password_hash = PasswordHashVO("hashed_password_123")
        user_code = UserCodeVO("ADMIN123")

        # Act
        user = User.create(
            email=email,
            hash_password=password_hash,
            user_code=user_code,
            role=UserRoleEnum.ADMIN,
            name="Admin",
            last_name="User",
        )

        # Assert
        assert user.role == UserRoleEnum.ADMIN

    @pytest.mark.unit
    def test_user_creation_with_suspended_state(self):
        """Test creating a user with suspended state."""
        # Arrange
        email = EmailVO("suspended@example.com")
        password_hash = PasswordHashVO("hashed_password_123")
        user_code = UserCodeVO("SUSP123")

        # Act
        user = User.create(
            email=email,
            hash_password=password_hash,
            user_code=user_code,
            state=UserStateEnum.SUSPENDED,
            name="Suspended",
            last_name="User",
        )

        # Assert
        assert user.state == UserStateEnum.SUSPENDED

    @pytest.mark.unit
    def test_user_equality(self):
        """Test user equality comparison."""
        # Arrange
        email1 = EmailVO("test1@example.com")
        password_hash1 = PasswordHashVO("hashed_password_123")
        user_code1 = UserCodeVO("USER123")

        email2 = EmailVO("test2@example.com")
        password_hash2 = PasswordHashVO("hashed_password_456")
        user_code2 = UserCodeVO("USER456")

        user1 = User.create(
            email=email1,
            hash_password=password_hash1,
            user_code=user_code1,
            name="Test1",
            last_name="User",
        )

        user2 = User.create(
            email=email2,
            hash_password=password_hash2,
            user_code=user_code2,
            name="Test2",
            last_name="User",
        )

        # Act & Assert
        assert user1 != user2
        assert user1 == user1
        assert user2 == user2

    @pytest.mark.unit
    def test_user_property_setters(self):
        """Test user property setters."""
        # Arrange
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

        # Act & Assert - Email setter
        new_email = EmailVO("new@example.com")
        user.email = new_email
        assert user.email == new_email

        # Act & Assert - Password setter
        new_password = PasswordHashVO("new_hashed_password")
        user.hash_password = new_password
        assert user.hash_password == new_password

        # Act & Assert - State setter
        user.state = UserStateEnum.SUSPENDED
        assert user.state == UserStateEnum.SUSPENDED

        # Act & Assert - Role setter
        user.role = UserRoleEnum.ADMIN
        assert user.role == UserRoleEnum.ADMIN

        # Act & Assert - User code setter
        new_user_code = UserCodeVO("NEW123")
        user.user_code = new_user_code
        assert user.user_code == new_user_code

    @pytest.mark.unit
    def test_user_property_setters_with_invalid_types(self):
        """Test user property setters with invalid types."""
        # Arrange
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

        # Act & Assert - Invalid email type
        with pytest.raises(ValueError, match="Email must be an instance of EmailVO"):
            user.email = "invalid_email"

        # Act & Assert - Invalid password type
        with pytest.raises(
            ValueError, match="Hash password must be an instance of PasswordHashVO"
        ):
            user.hash_password = "invalid_password"

        # Act & Assert - Invalid state type
        with pytest.raises(
            ValueError, match="State must be an instance of UserStateEnum"
        ):
            user.state = "INVALID_STATE"

        # Act & Assert - Invalid role type
        with pytest.raises(
            ValueError, match="Role must be an instance of UserRoleEnum"
        ):
            user.role = "INVALID_ROLE"

        # Act & Assert - Invalid user code type
        with pytest.raises(
            ValueError, match="User code must be an instance of UserCodeVO"
        ):
            user.user_code = "invalid_code"

    @pytest.mark.unit
    def test_user_hash(self):
        """Test user hash function."""
        # Arrange
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

        # Act & Assert
        assert hash(user) == hash(user.id)
        assert hash(user) != hash("some_string")

    @pytest.mark.unit
    def test_user_creation_with_invalid_email(self):
        """Test user creation with invalid email."""
        # Arrange
        invalid_email = EmailVO("invalid-email")
        password_hash = PasswordHashVO("hashed_password_123")
        user_code = UserCodeVO("USER123")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email"):
            User.create(
                email=invalid_email,
                hash_password=password_hash,
                user_code=user_code,
                name="Test",
                last_name="User",
            )

    @pytest.mark.unit
    def test_user_creation_with_invalid_user_code(self):
        """Test user creation with invalid user code."""
        # Arrange
        email = EmailVO("test@example.com")
        password_hash = PasswordHashVO("hashed_password_123")
        invalid_user_code = UserCodeVO("INVALID")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid user code"):
            User.create(
                email=email,
                hash_password=password_hash,
                user_code=invalid_user_code,
                name="Test",
                last_name="User",
            )

    @pytest.mark.unit
    def test_user_creation_with_invalid_password_hash(self):
        """Test user creation with invalid password hash."""
        # Arrange
        email = EmailVO("test@example.com")
        invalid_password_hash = PasswordHashVO("")
        user_code = UserCodeVO("USER123")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid password hash"):
            User.create(
                email=email,
                hash_password=invalid_password_hash,
                user_code=user_code,
                name="Test",
                last_name="User",
            )
