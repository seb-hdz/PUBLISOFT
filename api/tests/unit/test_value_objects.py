import pytest
from modules.auth.domain.value_objects.vo import EmailVO, UserCodeVO, PasswordHashVO


@pytest.mark.unit
class TestEmailVO:
    """Test cases for EmailVO value object."""

    @pytest.mark.unit
    def test_valid_email_creation(self):
        """Test creating EmailVO with valid email."""
        # Arrange & Act
        email = EmailVO("test@example.com")

        # Assert
        assert email.email == "test@example.com"
        assert str(email) == "test@example.com"

    @pytest.mark.unit
    def test_invalid_email_creation(self):
        """Test creating EmailVO with invalid email."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            EmailVO("invalid-email")

    @pytest.mark.unit
    def test_email_validation_method(self):
        """Test email validation method."""
        # Arrange & Act & Assert - Valid emails
        assert EmailVO.is_valid_email("test@example.com") is True
        assert EmailVO.is_valid_email("user.name@domain.co.uk") is True
        assert EmailVO.is_valid_email("test+tag@example.com") is True

        # Arrange & Act & Assert - Invalid emails
        assert EmailVO.is_valid_email("invalid-email") is False
        assert EmailVO.is_valid_email("@example.com") is False
        assert EmailVO.is_valid_email("test@") is False
        assert EmailVO.is_valid_email("") is False
        assert EmailVO.is_valid_email(None) is False

    @pytest.mark.unit
    def test_email_equality(self):
        """Test email equality comparison."""
        # Arrange
        email1 = EmailVO("test@example.com")
        email2 = EmailVO("test@example.com")
        email3 = EmailVO("different@example.com")

        # Act & Assert
        assert email1 == email2
        assert email1 != email3
        assert email1 == "test@example.com"

    @pytest.mark.unit
    def test_email_hash(self):
        """Test email hash function."""
        # Arrange
        email1 = EmailVO("test@example.com")
        email2 = EmailVO("test@example.com")
        email3 = EmailVO("different@example.com")

        # Act & Assert
        assert hash(email1) == hash(email2)
        assert hash(email1) != hash(email3)


@pytest.mark.unit
class TestUserCodeVO:
    """Test cases for UserCodeVO value object."""

    @pytest.mark.unit
    def test_valid_user_code_creation(self):
        """Test creating UserCodeVO with valid user code."""
        # Arrange & Act
        user_code = UserCodeVO("USER123")

        # Assert
        assert user_code.user_code == "USER123"
        assert str(user_code) == "USER123"

    @pytest.mark.unit
    def test_invalid_user_code_creation(self):
        """Test creating UserCodeVO with invalid user code."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid user code format"):
            UserCodeVO("INVALID")

    @pytest.mark.unit
    def test_user_code_validation_method(self):
        """Test user code validation method."""
        # Arrange & Act & Assert - Valid user codes
        assert UserCodeVO.is_valid_user_code("USER123") is True
        assert UserCodeVO.is_valid_user_code("ADMIN456") is True
        assert UserCodeVO.is_valid_user_code("STUDENT789") is True

        # Arrange & Act & Assert - Invalid user codes
        assert UserCodeVO.is_valid_user_code("INVALID") is False
        assert UserCodeVO.is_valid_user_code("123USER") is False
        assert UserCodeVO.is_valid_user_code("") is False
        assert UserCodeVO.is_valid_user_code(None) is False

    @pytest.mark.unit
    def test_user_code_equality(self):
        """Test user code equality comparison."""
        # Arrange
        code1 = UserCodeVO("USER123")
        code2 = UserCodeVO("USER123")
        code3 = UserCodeVO("USER456")

        # Act & Assert
        assert code1 == code2
        assert code1 != code3
        assert code1 == "USER123"

    @pytest.mark.unit
    def test_user_code_hash(self):
        """Test user code hash function."""
        # Arrange
        code1 = UserCodeVO("USER123")
        code2 = UserCodeVO("USER123")
        code3 = UserCodeVO("USER456")

        # Act & Assert
        assert hash(code1) == hash(code2)
        assert hash(code1) != hash(code3)


@pytest.mark.unit
class TestPasswordHashVO:
    """Test cases for PasswordHashVO value object."""

    @pytest.mark.unit
    def test_valid_password_hash_creation(self):
        """Test creating PasswordHashVO with valid password hash."""
        # Arrange & Act
        password_hash = PasswordHashVO("hashed_password_123")

        # Assert
        assert password_hash.hash_password == "hashed_password_123"
        assert str(password_hash) == "hashed_password_123"

    @pytest.mark.unit
    def test_invalid_password_hash_creation(self):
        """Test creating PasswordHashVO with invalid password hash."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Password hash cannot be empty"):
            PasswordHashVO("")

    @pytest.mark.unit
    def test_password_hash_validation_method(self):
        """Test password hash validation method."""
        # Arrange & Act & Assert - Valid password hashes
        assert PasswordHashVO.is_valid_hash_password("hashed_password_123") is True
        assert (
            PasswordHashVO.is_valid_hash_password(
                "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i"
            )
            is True
        )

        # Arrange & Act & Assert - Invalid password hashes
        assert PasswordHashVO.is_valid_hash_password("") is False
        assert PasswordHashVO.is_valid_hash_password(None) is False

    @pytest.mark.unit
    def test_password_hash_equality(self):
        """Test password hash equality comparison."""
        # Arrange
        hash1 = PasswordHashVO("hashed_password_123")
        hash2 = PasswordHashVO("hashed_password_123")
        hash3 = PasswordHashVO("different_hash_456")

        # Act & Assert
        assert hash1 == hash2
        assert hash1 != hash3
        assert hash1 == "hashed_password_123"

    @pytest.mark.unit
    def test_password_hash_hash(self):
        """Test password hash hash function."""
        # Arrange
        hash1 = PasswordHashVO("hashed_password_123")
        hash2 = PasswordHashVO("hashed_password_123")
        hash3 = PasswordHashVO("different_hash_456")

        # Act & Assert
        assert hash(hash1) == hash(hash2)
        assert hash(hash1) != hash(hash3)
