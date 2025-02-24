import pytest
from unittest.mock import patch, MagicMock
from util.speedtest_util import VPNTester

@pytest.fixture
def vpn_tester():
    return VPNTester()

@patch.object(VPNTester, 'run_command')
def test_get_vpn_status(mock_run_command, vpn_tester):
    """Test to check if vpn status outputs are correct"""
    # Simulate VPN status outputs
    mock_run_command.return_value = "Connected to Canada"
    assert vpn_tester.get_vpn_status() == "connected"
    
    mock_run_command.return_value = "Disconnected"
    assert vpn_tester.get_vpn_status() == "disconnected"
    
    mock_run_command.return_value = "Failed to connect"
    assert vpn_tester.get_vpn_status() == "unknown"

@patch.object(VPNTester, 'run_command')
@patch.object(VPNTester, 'get_vpn_alias', return_value="vpn_alias")
def test_measure_connection_time(mock_get_vpn_alias, mock_run_command, vpn_tester):
    """Test to check if connection is successful for valid and invalid server locations"""
    # Simulate successful connections
    mock_run_command.return_value = "Connected successfully"
    result = vpn_tester.measure_connection_time("United States", "New Jersey - 1", max_retries=1)
    assert result is not None and isinstance(result, float)
    result = vpn_tester.measure_connection_time("Japan", "Tokyo", max_retries=1)
    assert result is not None and isinstance(result, float)
    
    # Simulate invalid server locations
    mock_run_command.return_value = "Failed to connect"
    result = vpn_tester.measure_connection_time("USA", "New York", max_retries=1)
    assert result is None
    result = vpn_tester.measure_connection_time("Japan", "Chiyoda", max_retries=1)
    assert result is None

@patch.object(VPNTester, 'run_command')
def test_get_speedtest(mock_run_command, vpn_tester):
    """Test to check output from speedtest-cli"""
    # Simulate a successful speedtest JSON response
    mock_run_command.return_value = '{"download": 50000000}'  # 50 Mbps
    assert vpn_tester.get_speedtest() == 50.0
    
    # Simulate an error in JSON decoding
    mock_run_command.return_value = 'Invalid JSON'
    assert vpn_tester.get_speedtest() == 0
    
    # Simulate a 403 error response
    mock_run_command.return_value = '403 Forbidden'
    assert vpn_tester.get_speedtest() == 0
