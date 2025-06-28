import pytest
from unittest.mock import Mock, patch
from modules.auth.application.message_bus import MessageBus
from modules.auth.domain.commands.user_commands import RegisterUserCommand, LoginUserCommand
from modules.auth.application.handlers.commands.user_command_handlers import RegisterUserCommandHandler, LoginUserCommandHandler
from modules.auth.domain.entities.user import User, UserStateEnum, UserRoleEnum
from modules.auth.domain.value_objects.vo import EmailVO, UserCodeVO, PasswordHashVO
from common.exceptions import APIHTTPException


@pytest.mark.unit
@pytest.mark.auth
class TestMessageBus:
    """Test cases for the MessageBus."""

    @pytest.mark.unit
    def test_message_bus_initialization(self):
        """Test MessageBus initialization."""
        # Arrange & Act
        message_bus = MessageBus()
        
        # Assert
        assert message_bus is not None
        assert hasattr(message_bus, 'handlers')

    @pytest.mark.unit
    def test_register_handler(self):
        """Test registering a command handler."""
        # Arrange
        message_bus = MessageBus()
        handler = Mock()
        
        # Act
        message_bus.register_handler(RegisterUserCommand, handler)
        
        # Assert
        assert RegisterUserCommand in message_bus.handlers
        assert message_bus.handlers[RegisterUserCommand] == handler

    @pytest.mark.unit
    def test_handle_register_user_command(self, mock_unit_of_work):
        """Test handling RegisterUserCommand."""
        # Arrange
        message_bus = MessageBus()
        handler = RegisterUserCommandHandler()
        message_bus.register_handler(RegisterUserCommand, handler)
        
        command = RegisterUserCommand(
            email="test@example.com",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Act
        result = message_bus.handle(command, mock_unit_of_work)
        
        # Assert
        assert result is None  # RegisterUserCommand doesn't return anything

    @pytest.mark.unit
    def test_handle_login_user_command(self, mock_unit_of_work):
        """Test handling LoginUserCommand."""
        # Arrange
        message_bus = MessageBus()
        handler = LoginUserCommandHandler()
        message_bus.register_handler(LoginUserCommand, handler)
        
        command = LoginUserCommand(
            email="test@example.com",
            password="testpassword123"
        )
        
        # Mock the handler to return a token
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"
        with patch.object(handler, 'handle', return_value=[mock_token]):
            # Act
            result = message_bus.handle(command, mock_unit_of_work)
            
            # Assert
            assert result == [mock_token]

    @pytest.mark.unit
    def test_handle_unregistered_command(self, mock_unit_of_work):
        """Test handling an unregistered command."""
        # Arrange
        message_bus = MessageBus()
        command = RegisterUserCommand(
            email="test@example.com",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="No handler registered for command"):
            message_bus.handle(command, mock_unit_of_work)

    @pytest.mark.unit
    def test_handle_with_handler_exception(self, mock_unit_of_work):
        """Test handling command when handler raises an exception."""
        # Arrange
        message_bus = MessageBus()
        mock_handler = Mock()
        mock_handler.handle.side_effect = Exception("Handler error")
        message_bus.register_handler(RegisterUserCommand, mock_handler)
        
        command = RegisterUserCommand(
            email="test@example.com",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="Handler error"):
            message_bus.handle(command, mock_unit_of_work)


@pytest.mark.unit
@pytest.mark.auth
class TestRegisterUserCommandHandler:
    """Test cases for RegisterUserCommandHandler."""

    @pytest.mark.unit
    def test_handle_register_user_success(self, mock_unit_of_work):
        """Test successful user registration."""
        # Arrange
        handler = RegisterUserCommandHandler()
        command = RegisterUserCommand(
            email="test@example.com",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Mock the user repository
        mock_repository = Mock()
        mock_unit_of_work.users = mock_repository
        
        # Act
        result = handler.handle(command, mock_unit_of_work)
        
        # Assert
        assert result is None
        mock_repository.add.assert_called_once()
        
        # Verify the user was created with correct data
        created_user = mock_repository.add.call_args[0][0]
        assert isinstance(created_user, User)
        assert created_user.email.email == "test@example.com"
        assert created_user.role == UserRoleEnum.STUDENT
        assert created_user.state == UserStateEnum.ACTIVE

    @pytest.mark.unit
    def test_handle_register_user_with_existing_email(self, mock_unit_of_work):
        """Test user registration with existing email."""
        # Arrange
        handler = RegisterUserCommandHandler()
        command = RegisterUserCommand(
            email="existing@example.com",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Mock the user repository to simulate existing user
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = Mock()  # Existing user
        mock_unit_of_work.users = mock_repository
        
        # Act & Assert
        with pytest.raises(APIHTTPException) as exc_info:
            handler.handle(command, mock_unit_of_work)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @pytest.mark.unit
    def test_handle_register_user_with_invalid_data(self, mock_unit_of_work):
        """Test user registration with invalid data."""
        # Arrange
        handler = RegisterUserCommandHandler()
        command = RegisterUserCommand(
            email="invalid-email",
            password="testpassword123",
            name="Test",
            last_name="User"
        )
        
        # Mock the user repository
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = None
        mock_unit_of_work.users = mock_repository
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email"):
            handler.handle(command, mock_unit_of_work)


@pytest.mark.unit
@pytest.mark.auth
class TestLoginUserCommandHandler:
    """Test cases for LoginUserCommandHandler."""

    @pytest.mark.unit
    def test_handle_login_user_success(self, mock_unit_of_work):
        """Test successful user login."""
        # Arrange
        handler = LoginUserCommandHandler()
        command = LoginUserCommand(
            email="test@example.com",
            password="testpassword123"
        )
        
        # Create a mock user
        mock_user = Mock(spec=User)
        mock_user.email = EmailVO("test@example.com")
        mock_user.hash_password = PasswordHashVO("hashed_password")
        mock_user.state = UserStateEnum.ACTIVE
        
        # Mock the user repository
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = mock_user
        mock_unit_of_work.users = mock_repository
        
        # Mock password verification
        with patch('modules.auth.domain.services.user_services.verify_password', return_value=True):
            with patch('modules.auth.domain.services.user_services.generate_jwt_token', return_value="test_token"):
                # Act
                result = handler.handle(command, mock_unit_of_work)
                
                # Assert
                assert result == ["test_token"]
                mock_repository.get_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.unit
    def test_handle_login_user_not_found(self, mock_unit_of_work):
        """Test login with non-existent user."""
        # Arrange
        handler = LoginUserCommandHandler()
        command = LoginUserCommand(
            email="nonexistent@example.com",
            password="testpassword123"
        )
        
        # Mock the user repository
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = None
        mock_unit_of_work.users = mock_repository
        
        # Act & Assert
        with pytest.raises(APIHTTPException) as exc_info:
            handler.handle(command, mock_unit_of_work)
        
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.unit
    def test_handle_login_user_invalid_password(self, mock_unit_of_work):
        """Test login with invalid password."""
        # Arrange
        handler = LoginUserCommandHandler()
        command = LoginUserCommand(
            email="test@example.com",
            password="wrongpassword"
        )
        
        # Create a mock user
        mock_user = Mock(spec=User)
        mock_user.email = EmailVO("test@example.com")
        mock_user.hash_password = PasswordHashVO("hashed_password")
        mock_user.state = UserStateEnum.ACTIVE
        
        # Mock the user repository
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = mock_user
        mock_unit_of_work.users = mock_repository
        
        # Mock password verification to return False
        with patch('modules.auth.domain.services.user_services.verify_password', return_value=False):
            # Act & Assert
            with pytest.raises(APIHTTPException) as exc_info:
                handler.handle(command, mock_unit_of_work)
            
            assert exc_info.value.status_code == 401
            assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.unit
    def test_handle_login_user_suspended(self, mock_unit_of_work):
        """Test login with suspended user."""
        # Arrange
        handler = LoginUserCommandHandler()
        command = LoginUserCommand(
            email="suspended@example.com",
            password="testpassword123"
        )
        
        # Create a mock suspended user
        mock_user = Mock(spec=User)
        mock_user.email = EmailVO("suspended@example.com")
        mock_user.hash_password = PasswordHashVO("hashed_password")
        mock_user.state = UserStateEnum.SUSPENDED
        
        # Mock the user repository
        mock_repository = Mock()
        mock_repository.get_by_email.return_value = mock_user
        mock_unit_of_work.users = mock_repository
        
        # Act & Assert
        with pytest.raises(APIHTTPException) as exc_info:
            handler.handle(command, mock_unit_of_work)
        
        assert exc_info.value.status_code == 401
        assert "Account is suspended" in exc_info.value.detail 