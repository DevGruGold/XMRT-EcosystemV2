import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { 
  Brain, 
  Coins, 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Shield, 
  Network,
  Lock,
  Zap,
  Globe,
  Database,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [proposal, setProposal] = useState('')
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: "Hello! I'm Eliza, the advanced AI brain behind XMRT DAO. I can help with governance, cross-chain operations, ZK proofs, and treasury optimization. How can I assist you today?" }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [useZkAnalysis, setUseZkAnalysis] = useState(false)
  const [selectedChain, setSelectedChain] = useState('ethereum')
  const [bridgeAmount, setBridgeAmount] = useState('')
  const [targetChain, setTargetChain] = useState('polygon')

  // Enhanced capabilities state
  const [capabilities, setCapabilities] = useState({
    natural_language: true,
    cross_chain: true,
    zero_knowledge: true,
    verifiable_compute: true,
    oracle_integration: true,
    autonomous_execution: true
  })

  const [services, setServices] = useState({
    cross_chain: 'checking...',
    zk_service: 'checking...',
    storage: 'checking...'
  })

  useEffect(() => {
    // Simulate service status checks
    setTimeout(() => {
      setServices({
        cross_chain: 'active',
        zk_service: 'active',
        storage: 'active'
      })
    }, 2000)
  }, [])

  const sendMessage = async () => {
    if (!message.trim()) return

    setIsLoading(true)
    const userMessage = { role: 'user', content: message }
    setChatHistory(prev => [...prev, userMessage])

    try {
      // Simulate API call to Eliza
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const elizaResponse = {
        role: 'assistant',
        content: `I understand you're asking about: "${message}". Based on my enhanced capabilities including cross-chain operations, ZK proofs, and verifiable computation, I can help you with this request. Would you like me to analyze this using zero-knowledge proofs for privacy, or execute any cross-chain operations?`,
        message_type: 'general',
        autonomous_actions: []
      }

      setChatHistory(prev => [...prev, elizaResponse])
    } catch (error) {
      const errorResponse = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.'
      }
      setChatHistory(prev => [...prev, errorResponse])
    }

    setMessage('')
    setIsLoading(false)
  }

  const analyzeProposal = async () => {
    if (!proposal.trim()) return

    setIsLoading(true)
    try {
      // Simulate proposal analysis
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const analysisType = useZkAnalysis ? 'ZK-verified' : 'standard'
      alert(`Proposal analyzed using ${analysisType} analysis. Results would be displayed here in a real implementation.`)
    } catch (error) {
      alert('Error analyzing proposal. Please try again.')
    }
    setIsLoading(false)
  }

  const executeCrossChainBridge = async () => {
    if (!bridgeAmount) return

    setIsLoading(true)
    try {
      // Simulate cross-chain bridge operation
      await new Promise(resolve => setTimeout(resolve, 2000))
      alert(`Cross-chain bridge operation initiated: ${bridgeAmount} XMRT from ${selectedChain} to ${targetChain}`)
    } catch (error) {
      alert('Error executing cross-chain operation. Please try again.')
    }
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">XMRT DAO</h1>
              <Badge variant="secondary">v2.0 Enhanced</Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="flex items-center space-x-1">
                <Network className="h-3 w-3" />
                <span>Multi-Chain</span>
              </Badge>
              <Badge variant="outline" className="flex items-center space-x-1">
                <Lock className="h-3 w-3" />
                <span>ZK-Enabled</span>
              </Badge>
              <Button variant="outline">Connect Wallet</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Advanced Multi-Chain AI DAO
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
            Powered by Enhanced Eliza AI with Cross-Chain, ZK Proofs, and Verifiable Computation
          </p>
          <div className="flex justify-center space-x-4">
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Coins className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
                <p className="font-semibold">21M XMRT</p>
                <p className="text-sm text-gray-600">Omnichain Supply</p>
              </CardContent>
            </Card>
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Network className="h-8 w-8 mx-auto mb-2 text-green-600" />
                <p className="font-semibold">6 Chains</p>
                <p className="text-sm text-gray-600">Supported</p>
              </CardContent>
            </Card>
            <Card className="w-48">
              <CardContent className="p-4 text-center">
                <Lock className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                <p className="font-semibold">ZK Privacy</p>
                <p className="text-sm text-gray-600">Enabled</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Service Status */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between">
                <span>Cross-Chain Service</span>
                <Badge variant={services.cross_chain === 'active' ? 'default' : 'secondary'}>
                  {services.cross_chain === 'active' ? <CheckCircle className="h-3 w-3 mr-1" /> : <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                  {services.cross_chain}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>ZK Service</span>
                <Badge variant={services.zk_service === 'active' ? 'default' : 'secondary'}>
                  {services.zk_service === 'active' ? <CheckCircle className="h-3 w-3 mr-1" /> : <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                  {services.zk_service}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Storage Service</span>
                <Badge variant={services.storage === 'active' ? 'default' : 'secondary'}>
                  {services.storage === 'active' ? <CheckCircle className="h-3 w-3 mr-1" /> : <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                  {services.storage}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Interface */}
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="governance">Governance</TabsTrigger>
            <TabsTrigger value="eliza">Enhanced Eliza</TabsTrigger>
            <TabsTrigger value="cross-chain">Cross-Chain</TabsTrigger>
            <TabsTrigger value="zk-privacy">ZK Privacy</TabsTrigger>
            <TabsTrigger value="agents">AI Agents</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Coins className="h-5 w-5 mr-2" />
                    Total Balance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">0 XMRT</p>
                  <p className="text-sm text-gray-600">Across all chains</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2" />
                    Staked Amount
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">0 XMRT</p>
                  <p className="text-sm text-gray-600">Multi-chain staking</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="h-5 w-5 mr-2" />
                    Eliza Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-green-600">Enhanced Active</Badge>
                  <p className="text-sm text-gray-600 mt-2">All capabilities online</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Database className="h-5 w-5 mr-2" />
                    Treasury Value
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">$1.5M</p>
                  <p className="text-sm text-gray-600">Optimized by AI</p>
                </CardContent>
              </Card>
            </div>

            {/* Capabilities Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Enhanced Capabilities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(capabilities).map(([key, enabled]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <CheckCircle className={`h-4 w-4 ${enabled ? 'text-green-600' : 'text-gray-400'}`} />
                      <span className="capitalize">{key.replace('_', ' ')}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="governance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Enhanced Proposal Submission</CardTitle>
                <CardDescription>
                  Submit proposals with optional ZK privacy and verifiable analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Describe your proposal here..."
                  value={proposal}
                  onChange={(e) => setProposal(e.target.value)}
                  className="min-h-32"
                />
                <div className="flex items-center space-x-2">
                  <Switch
                    id="zk-analysis"
                    checked={useZkAnalysis}
                    onCheckedChange={setUseZkAnalysis}
                  />
                  <Label htmlFor="zk-analysis">Use ZK-verified analysis (RISC Zero)</Label>
                </div>
                <Button 
                  className="w-full" 
                  onClick={analyzeProposal}
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Submit for {useZkAnalysis ? 'ZK-Verified' : 'Standard'} Analysis
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Proposals</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">No active proposals. Submit the first one above!</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="eliza" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageSquare className="h-5 w-5 mr-2" />
                  Enhanced Eliza AI
                </CardTitle>
                <CardDescription>
                  Advanced AI with cross-chain, ZK, and verifiable computation capabilities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="h-96 border rounded-lg p-4 bg-gray-50 dark:bg-gray-800 overflow-y-auto">
                  {chatHistory.map((msg, index) => (
                    <div key={index} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      <div className={`inline-block p-3 rounded-lg max-w-[80%] ${
                        msg.role === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white dark:bg-gray-700 border'
                      }`}>
                        <p className="text-sm">{msg.content}</p>
                        {msg.autonomous_actions && msg.autonomous_actions.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-gray-200">
                            <p className="text-xs text-gray-500">Autonomous actions triggered</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="text-left">
                      <div className="inline-block p-3 rounded-lg bg-white dark:bg-gray-700 border">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Ask about cross-chain ops, ZK proofs, treasury optimization..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={sendMessage} disabled={isLoading}>
                    {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Send'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="cross-chain" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Network className="h-5 w-5 mr-2" />
                  Cross-Chain Bridge
                </CardTitle>
                <CardDescription>
                  Bridge XMRT tokens across supported networks using Wormhole and LayerZero
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>From Chain</Label>
                    <Select value={selectedChain} onValueChange={setSelectedChain}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ethereum">Ethereum</SelectItem>
                        <SelectItem value="polygon">Polygon</SelectItem>
                        <SelectItem value="bsc">BSC</SelectItem>
                        <SelectItem value="avalanche">Avalanche</SelectItem>
                        <SelectItem value="arbitrum">Arbitrum</SelectItem>
                        <SelectItem value="optimism">Optimism</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>To Chain</Label>
                    <Select value={targetChain} onValueChange={setTargetChain}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ethereum">Ethereum</SelectItem>
                        <SelectItem value="polygon">Polygon</SelectItem>
                        <SelectItem value="bsc">BSC</SelectItem>
                        <SelectItem value="avalanche">Avalanche</SelectItem>
                        <SelectItem value="arbitrum">Arbitrum</SelectItem>
                        <SelectItem value="optimism">Optimism</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Amount (XMRT)</Label>
                  <Input
                    type="number"
                    placeholder="0.0"
                    value={bridgeAmount}
                    onChange={(e) => setBridgeAmount(e.target.value)}
                  />
                </div>
                <Button 
                  className="w-full" 
                  onClick={executeCrossChainBridge}
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Bridge Tokens
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cross-Chain Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Wormhole Bridge</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>LayerZero OFT</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Supported Chains</span>
                    <Badge variant="outline">6 Networks</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="zk-privacy" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lock className="h-5 w-5 mr-2" />
                  Zero-Knowledge Privacy
                </CardTitle>
                <CardDescription>
                  Private voting, verifiable computation, and oracle verification
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Noir Circuits</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge variant="default" className="mb-2">Active</Badge>
                      <p className="text-sm text-gray-600">Private voting and governance</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">RISC Zero</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge variant="default" className="mb-2">Active</Badge>
                      <p className="text-sm text-gray-600">Verifiable computation</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">ZK Oracles</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge variant="default" className="mb-2">Active</Badge>
                      <p className="text-sm text-gray-600">TLSNotary verification</p>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Generate ZK Proof</CardTitle>
              </CardHeader>
              <CardContent>
                <Button className="w-full" disabled>
                  Generate Private Vote Proof (Demo)
                </Button>
                <p className="text-sm text-gray-600 mt-2">
                  In production, this would generate a zero-knowledge proof for private voting
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="agents" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Governance Agent</CardTitle>
                  <CardDescription>Enhanced with ZK privacy and cross-chain capabilities</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-blue-600 mb-2">Enhanced Active</Badge>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>• Private proposal analysis</p>
                    <p>• Cross-chain governance</p>
                    <p>• Verifiable voting</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Treasury Agent</CardTitle>
                  <CardDescription>AI-powered multi-chain treasury optimization</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-green-600 mb-2">Enhanced Active</Badge>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>• RISC Zero optimization</p>
                    <p>• Cross-chain rebalancing</p>
                    <p>• Yield farming automation</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Community Agent</CardTitle>
                  <CardDescription>24/7 support with advanced AI capabilities</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="default" className="bg-purple-600 mb-2">Enhanced Active</Badge>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>• Multi-language support</p>
                    <p>• Technical assistance</p>
                    <p>• Educational content</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Governance Efficiency</span>
                      <span className="text-sm">95%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{width: '95%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Treasury Performance</span>
                      <span className="text-sm">87%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{width: '87%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Community Satisfaction</span>
                      <span className="text-sm">92%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-purple-600 h-2 rounded-full" style={{width: '92%'}}></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm dark:bg-gray-900/80 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              XMRT DAO v2.0 - Enhanced with Cross-Chain, ZK Privacy & Verifiable AI
            </p>
            <div className="flex space-x-4">
              <Badge variant="outline">Contract: 0x77307...a15</Badge>
              <Badge variant="outline">Multi-Chain</Badge>
              <Badge variant="outline">ZK-Enabled</Badge>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
