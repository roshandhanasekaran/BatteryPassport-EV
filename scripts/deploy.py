# scripts/deploy.py
from brownie import MockV3Aggregator
from brownie import EVBatteryPassportLite,EVBatteryPassportBatch, MockV3Aggregator, network, config
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie.network.contract import Contract


def estimate_gas():
    account = get_account()
    # Assuming mocks are deployed already
    price_feed_address = MockV3Aggregator[-1].address
    government_address = account.address

    # Estimate gas for EVBatteryPassportLite
    estimated_gas = EVBatteryPassportLite.deploy.estimate_gas(
        government_address,
        price_feed_address,
        {"from": account}
    )

    print(f"Estimated Gas: {estimated_gas}")
    return estimated_gas


def deploy_ev_battery_passport_lite():
    """
    Deploys the EVBatteryPassportLite contract.

    - Deploys mock contracts if on a local network.
    - Retrieves the appropriate price feed address.
    - Assumes the deployer account is the government.

    Returns:
        EVBatteryPassportLite: The deployed EVBatteryPassportLite contract instance.
    """
    account = get_account()
    
    # Deploy mocks if on a local blockchain
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print("Local network detected! Deploying mocks...")
        deploy_mocks()
        price_feed = MockV3Aggregator[-1]
        price_feed_address = price_feed.address
    else:
        # Use the real price feed address from config
        price_feed_address = config["networks"][network.show_active()]["eth_gbp_price_feed"]
    
    # Government address is the deployer account
    government_address = account.address
    
    # Estimate gas
    gas_estimate = EVBatteryPassportLite.constructor.estimateGas(government_address, price_feed_address)
    print(f"Estimated Gas: {gas_estimate}")

    # Deploy the EVBatteryPassportLite contract
    print(f"Deploying EVBatteryPassportLite from account {account}...")
    ev_battery_passport_lite = EVBatteryPassportLite.deploy(
        government_address,
        price_feed_address,
        {"from": account, "gas_limit": 3000000},  # Adjust this value as needed
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    
    print(f"EVBatteryPassportLite deployed at {ev_battery_passport_lite.address}")
    return ev_battery_passport_lite


def main():
    """
    The main function that Brownie calls when deploying.
    """
    deploy_ev_battery_passport_lite()
