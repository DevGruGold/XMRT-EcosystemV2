
        const HDWalletProvider = require('@truffle/hdwallet-provider');
        
        module.exports = {
          networks: {
            sepolia: {
              provider: () => new HDWalletProvider(
                "2945003529e7268a5c01e9ed7ef73ffa066fe2e62af24fe073e97c477c65d324",
                "https://sepolia.infura.io/v3/c843a693bc5d43d1aee471d2491f2414"
              ),
              network_id: 11155111,
              gas: 5500000,
              confirmations: 2,
              timeoutBlocks: 200,
              skipDryRun: true
            }
          },
          compilers: {
            solc: {
              version: "0.8.0",
              settings: {
                optimizer: {
                  enabled: true,
                  runs: 200
                }
              }
            }
          }
        };
        