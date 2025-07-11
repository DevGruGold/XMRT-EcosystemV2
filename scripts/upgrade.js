
    const Governance = artifacts.require('Governance');
    const GovernanceUpgrade = artifacts.require('GovernanceUpgrade');
    
    module.exports = async function (callback) {
        try {
            const proxyAddress = process.argv[4];
            const newImplementationAddress = process.argv[5];
            
            console.log(`Upgrading proxy at ${proxyAddress} to new implementation...`);
            
            const proxy = await Governance.at(proxyAddress);
            await proxy.upgradeTo(newImplementationAddress);
            
            console.log('Upgrade completed successfully!');
            callback();
        } catch (e) {
            console.error('Upgrade failed:', e);
            callback(e);
        }
    };
    