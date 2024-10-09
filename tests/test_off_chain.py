import pytest
from brownie import accounts, Wei, reverts
import requests

@pytest.fixture
def government_account():
    return accounts[0]

@pytest.fixture
def manufacturer_account():
    return accounts[1]

@pytest.fixture
def supplier_account():
    return accounts[2]

@pytest.fixture
def consumer_account():
    return accounts[3]

@pytest.fixture
def recycler_account():
    return accounts[4]

def retrieve_off_chain_data(ipfs_hash):
    """Function to retrieve data from IPFS using the IPFS hash."""
    ipfs_gateway_url = f"https://ipfs.io/ipfs/{ipfs_hash}"  # IPFS gateway URL
    try:
        response = requests.get(ipfs_gateway_url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Assuming off-chain data is stored as JSON
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve IPFS data: {e}")
        return None

def test_retrieve_off_chain_data(ev_battery_passport, government_account, manufacturer_account, supplier_account, consumer_account, recycler_account):
    """Test to retrieve off-chain data from IPFS and display it with on-chain details."""

    # Adding a manufacturer and locking deposit
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    min_deposit_in_wei = ev_battery_passport.calculateMinDeposit({'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': min_deposit_in_wei})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})

    # Manufacturer sets battery data and mints token with updated IPFS hash
    token_id = 1
    off_chain_data_hash = "QmPoEfuyhqEY7YZAmMmEoGc5Kco59EQ8kBQHfv6Q5a4CwQ"  # Updated IPFS hash with realistic battery data
    ev_battery_passport.setBatteryData(
        token_id,
        "Lithium-Ion",                    # Updated Battery Type (commonly used in EVs)
        "LGX200",                         # Updated Battery Model (Example model from a real manufacturer)
        "EV Power Battery Pack",          # Updated Product Name (Realistic product name)
        "Gigafactory 1, Nevada, USA",     # Updated Manufacturing Site (Tesla Gigafactory location)
        off_chain_data_hash,              # Updated offChainDataHash argument
        {'from': manufacturer_account}
    )

    # Consumer views battery details including the off-chain IPFS data
    batteryDetails = ev_battery_passport.viewBatteryDetails(token_id, {'from': consumer_account})

    # Unpack on-chain battery details
    batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer, offChainDataHash = batteryDetails

    # Print on-chain data
    print("=== On-Chain Battery Details ===")
    print(f"Battery Type: {batteryType}")
    print(f"Battery Model: {batteryModel}")
    print(f"Product Name: {productName}")
    print(f"Manufacturing Site: {manufacturingSite}")
    print(f"Supply Chain Info: {supplyChainInfo}")
    print(f"Recycled: {'Yes' if isRecycled else 'No'}")
    print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer else 'No'}")
    print(f"Off-Chain Data Hash: {offChainDataHash}")

    # Fetch and print off-chain data from IPFS
    off_chain_data = retrieve_off_chain_data(offChainDataHash)
    if off_chain_data:
        print("=== Off-Chain Data (from IPFS) ===")
        print(off_chain_data)
    else:
        print("Failed to retrieve off-chain data.")
        
        
