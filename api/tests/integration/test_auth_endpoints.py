import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from modules.auth.domain.commands.user_commands import (
    RegisterUserCommand,
    LoginUserCommand,
)
from common.exceptions import APIHTTPException


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    @pytest.mark.integration
    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        # Arrange
        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.return_value = None

            # Act
            response = client.post("/auth/register", json=sample_user_data)

            # Assert
            assert response.status_code == 201
            assert response.json() == {"message": "User registered successfully"}

            # Verify the command was created and handled correctly
            mock_handle.assert_called_once()
            call_args = mock_handle.call_args
            command = call_args[0][0]  # First argument is the command
            assert isinstance(command, RegisterUserCommand)
            assert command.email == sample_user_data["email"]
            assert command.password == sample_user_data["password"]
            assert command.name == sample_user_data["name"]
            assert command.last_name == sample_user_data["last_name"]

    @pytest.mark.integration
    def test_register_user_with_invalid_data(self, client):
        """Test user registration with invalid data."""
        # Arrange
        invalid_data = {
            "email": "invalid-email",
            "password": "short",
            "name": "",
            "last_name": "",
        }

        # Act
        response = client.post("/auth/register", json=invalid_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_register_user_with_missing_data(self, client):
        """Test user registration with missing required fields."""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password, name, last_name
        }

        # Act
        response = client.post("/auth/register", json=incomplete_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_register_user_api_exception(self, client, sample_user_data):
        """Test user registration when API exception is raised."""
        # Arrange
        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.side_effect = APIHTTPException(
                status_code=400, detail="User already exists"
            )

            # Act
            response = client.post("/auth/register", json=sample_user_data)

            # Assert
            assert response.status_code == 400
            assert response.json() == {"detail": "User already exists"}

    @pytest.mark.integration
    def test_register_user_unexpected_exception(self, client, sample_user_data):
        """Test user registration when unexpected exception is raised."""
        # Arrange
        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.side_effect = Exception("Database connection failed")

            # Act
            response = client.post("/auth/register", json=sample_user_data)

            # Assert
            assert response.status_code == 500
            assert response.json() == {"detail": "An unexpected error occurred"}

    @pytest.mark.integration
    def test_login_user_success(self, client, sample_login_data):
        """Test successful user login."""
        # Arrange
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"

        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.return_value = [mock_token]

            # Act
            response = client.post("/auth/login", json=sample_login_data)

            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Login successful"
            assert response_data["accesstoken"] == mock_token

            # Verify the command was created and handled correctly
            mock_handle.assert_called_once()
            call_args = mock_handle.call_args
            command = call_args[0][0]  # First argument is the command
            assert isinstance(command, LoginUserCommand)
            assert command.email == sample_login_data["email"]
            assert command.password == sample_login_data["password"]

            # Verify cookie was set
            cookies = response.cookies
            assert "accesstoken" in cookies
            assert cookies["accesstoken"].value == mock_token
            assert cookies["accesstoken"]["httponly"] is True

    @pytest.mark.integration
    def test_login_user_with_invalid_data(self, client):
        """Test user login with invalid data."""
        # Arrange
        invalid_data = {"email": "invalid-email", "password": ""}

        # Act
        response = client.post("/auth/login", json=invalid_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_login_user_with_missing_data(self, client):
        """Test user login with missing required fields."""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }

        # Act
        response = client.post("/auth/login", json=incomplete_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_login_user_api_exception(self, client, sample_login_data):
        """Test user login when API exception is raised."""
        # Arrange
        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.side_effect = APIHTTPException(
                status_code=401, detail="Invalid credentials"
            )

            # Act
            response = client.post("/auth/login", json=sample_login_data)

            # Assert
            assert response.status_code == 401
            assert response.json() == {"detail": "Invalid credentials"}

    @pytest.mark.integration
    def test_login_user_unexpected_exception(self, client, sample_login_data):
        """Test user login when unexpected exception is raised."""
        # Arrange
        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.side_effect = Exception("Database connection failed")

            # Act
            response = client.post("/auth/login", json=sample_login_data)

            # Assert
            assert response.status_code == 500
            assert response.json() == {"detail": "An unexpected error occurred"}

    @pytest.mark.integration
    def test_logout_success(self, client):
        """Test successful user logout."""
        # Act
        response = client.post("/auth/logout")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"msg": "Logout successful"}

        # Verify cookie was deleted
        cookies = response.cookies
        assert "accesstoken" in cookies
        assert cookies["accesstoken"].value == ""

    @pytest.mark.integration
    def test_register_user_with_extra_fields(self, client):
        """Test user registration with extra fields (should be ignored)."""
        # Arrange
        data_with_extra = {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test",
            "last_name": "User",
            "extra_field": "should_be_ignored",
        }

        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.return_value = None

            # Act
            response = client.post("/auth/register", json=data_with_extra)

            # Assert
            assert response.status_code == 201
            assert response.json() == {"message": "User registered successfully"}

    @pytest.mark.integration
    def test_login_user_with_extra_fields(self, client):
        """Test user login with extra fields (should be ignored)."""
        # Arrange
        data_with_extra = {
            "email": "test@example.com",
            "password": "testpassword123",
            "extra_field": "should_be_ignored",
        }

        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"

        with patch(
            "modules.auth.application.message_bus.MessageBus.handle"
        ) as mock_handle:
            mock_handle.return_value = [mock_token]

            # Act
            response = client.post("/auth/login", json=data_with_extra)

            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Login successful"
            assert response_data["accesstoken"] == mock_token
