import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

const App = () => {
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState('1,234.56');
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [agentActivities, setAgentActivities] = useState([]);

  // Wallet connection
  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();

        setWallet(accounts[0]);
        setConnected(true);

        // Check if on Sepolia
        const network = await provider.getNetwork();
        if (network.chainId !== 11155111n) {
          await switchToSepolia();
        }
      } catch (error) {
        console.error('Error connecting wallet:', error);
      }
    }
  };

  const switchToSepolia = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0xaa36a7' }],
      });
    } catch (error) {
      console.error('Error switching network:', error);
    }
  };

  // Simulate AI agent activities
  useEffect(() => {
    const activities = [
      { agent: 'Executive', action: 'Analyzing market conditions...', time: '2m ago' },
      { agent: 'Operations', action: 'Optimized mining efficiency by 12%', time: '5m ago' },
      { agent: 'Financial', action: 'Rebalanced treasury allocation', time: '8m ago' },
    ];
    setAgentActivities(activities);

    // Simulate real-time updates
    const interval = setInterval(() => {
      const newActivity = {
        agent: ['Executive', 'Operations', 'Financial'][Math.floor(Math.random() * 3)],
        action: [
          'Executing autonomous decision...',
          'Monitoring network performance...',
          'Optimizing yield strategies...',
          'Processing governance proposal...'
        ][Math.floor(Math.random() * 4)],
        time: 'now'
      };
      setAgentActivities(prev => [newActivity, ...prev.slice(0, 2)]);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="text-sm font-bold">📱</span>
            </div>
            <div>
              <h1 className="text-lg font-bold">MobileMonero</h1>
              <p className="text-xs text-gray-400">AI-Powered Mining DAO</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-xs text-green-500">Live</span>
            <button
              onClick={connectWallet}
              className="bg-green-500 text-black px-4 py-2 rounded-lg text-sm font-medium"
            >
              {connected ? `${wallet?.slice(0, 6)}...` : 'Connect Wallet'}
            </button>
          </div>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {/* Balance Card */}
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Your Balance</span>
            <div className="flex space-x-2">
              <button className="bg-green-500 text-black px-4 py-2 rounded-lg text-sm font-medium">
                Send
              </button>
              <button className="bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
                Receive
              </button>
            </div>
          </div>
          <div className="text-3xl font-bold mb-4">${balance}</div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded-lg p-3">
              <span className="text-sm text-gray-400">24h Change</span>
              <div className="text-green-500 font-semibold">+2.14%</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <span className="text-sm text-gray-400">Portfolio Value</span>
              <div className="text-white font-semibold">$5,678.90</div>
            </div>
          </div>
        </div>

        {/* Mining Revenue */}
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold">Mining Revenue</h3>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-500">Active</span>
            </div>
          </div>
          <div className="mb-3">
            <span className="text-sm text-gray-400">Today's Mining</span>
            <div className="text-green-500 font-semibold">+0.0247 XMR</div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
              <div className="bg-green-500 h-2 rounded-full" style={{width: '67%'}}></div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-lg font-bold">147</div>
              <div className="text-xs text-gray-400">Miners</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">2.3</div>
              <div className="text-xs text-gray-400">MH/s</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">$47.20</div>
              <div className="text-xs text-gray-400">Daily</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button className="bg-green-500 text-black py-2 rounded-lg text-sm font-medium flex items-center justify-center space-x-1">
              <span>⬇️</span>
              <span>Get XMRT Miner</span>
            </button>
            <button className="bg-blue-600 text-white py-2 rounded-lg text-sm font-medium flex items-center justify-center space-x-1">
              <span>🎁</span>
              <span>Get Test Tokens</span>
            </button>
          </div>
        </div>

        {/* AI Agents */}
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">AI Agents</h3>
            <span className="text-xs text-green-500">3 Active</span>
          </div>
          <div className="space-y-2">
            {agentActivities.map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-b-0">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">{activity.agent}:</span>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-300">{activity.action}</div>
                  <div className="text-xs text-gray-500">{activity.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bridge Widget */}
        <div className="bg-gray-800 rounded-xl p-4">
          <h3 className="font-semibold mb-3">Universal Bridge</h3>
          <div className="space-y-3">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">From</span>
                <span className="text-sm text-green-500">Balance: 0.5 ETH</span>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="0.0"
                  className="bg-transparent text-2xl font-bold flex-1 outline-none"
                />
                <div className="bg-gray-600 px-3 py-1 rounded-lg text-sm">ETH</div>
              </div>
            </div>
            <div className="flex justify-center">
              <button className="bg-gray-700 p-2 rounded-full">⇅</button>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">To</span>
                <span className="text-sm text-green-500">Rate: 1 ETH = 50 PI</span>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="0.0"
                  className="bg-transparent text-2xl font-bold flex-1 outline-none"
                />
                <div className="bg-gray-600 px-3 py-1 rounded-lg text-sm">PI</div>
              </div>
            </div>
            <button className="w-full bg-green-500 text-black py-3 rounded-lg font-semibold">
              Bridge Assets
            </button>
          </div>
        </div>

        {/* Staking */}
        <div className="bg-gray-800 rounded-xl p-4">
          <h3 className="font-semibold mb-3">XMRT Staking</h3>
          <div className="space-y-3">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Staked Amount</span>
                <span className="text-sm text-green-500">APY: 12.5%</span>
              </div>
              <div className="text-xl font-bold">1,250 XMRT</div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button className="bg-green-500 text-black py-2 rounded-lg text-sm font-medium">
                Stake More
              </button>
              <button className="bg-gray-700 text-white py-2 rounded-lg text-sm font-medium">
                Unstake
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center py-4 border-t border-gray-800 mt-8">
          <div className="flex justify-center space-x-4 mb-2">
            <a href="https://github.com/DevGruGold" className="text-gray-400 hover:text-green-500">
              <span className="text-lg">📂</span>
            </a>
            <a href="https://sepolia.etherscan.io/token/0x77307dfbc436224d5e6f2048d2b6bdfa66998a15" className="text-gray-400 hover:text-green-500">
              <span className="text-lg">🔍</span>
            </a>
          </div>
          <p className="text-xs text-gray-500">
            © 2025 MobileMonero DAO • IP tokenized as NFT • Contact: xmrtsolutions@gmail.com
          </p>
        </footer>
      </div>
    </div>
  );
};

export default App;