'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Bot, User, FileText, BarChart3, Loader2 } from 'lucide-react'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatResponse {
  response: string
  conversation_id?: string
}

export default function FloatingChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI fire monitoring assistant. I can help you with:\n\n🔥 Generate reports for authorities\n📊 Analyze fire statistics\n📍 Find top fires by power or location\n📈 Calculate fire trends\n\nWhat would you like to know?',
      timestamp: new Date().toISOString()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data: ChatResponse = await response.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check if the backend is running.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatMessage = (content: string) => {
    // Check if this is a report generation message that should have a download button
    const isReportMessage = content.includes('Fire Prediction Report') && content.includes('generated')
    
    // Simple formatting for better readability
    const formattedContent = content
      .split('\n')
      .map((line, index) => (
        <div key={index} className={line.trim() === '' ? 'h-2' : ''}>
          {line.startsWith('🔥') || line.startsWith('📊') || line.startsWith('📍') || line.startsWith('📈') ? (
            <div className="font-medium text-blue-600">{line}</div>
          ) : line.startsWith('**') && line.endsWith('**') ? (
            <div className="font-semibold">{line.replace(/\*\*/g, '')}</div>
          ) : line.startsWith('- ') || line.startsWith('• ') ? (
            <div className="ml-4 text-gray-700">{line}</div>
          ) : line.startsWith('✅') ? (
            <div className="text-green-600 font-medium">{line}</div>
          ) : (
            <div>{line}</div>
          )}
        </div>
      ))

    // Add download button for report messages OR prediction results
    const showDownloadButton = (isReportMessage && !content.includes('Downloaded Successfully')) || 
                               (content.includes('highest probability fire predictions') && content.includes('Probability:'))

    if (showDownloadButton) {
      return (
        <div>
          {formattedContent}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <button
              onClick={downloadPredictionReport}
              className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              <FileText className="w-4 h-4" />
              <span>Download PDF Report</span>
            </button>
            <p className="text-xs text-gray-500 mt-2">
              Generate official PDF report with these predictions for authorities
            </p>
          </div>
        </div>
      )
    }

    return <div>{formattedContent}</div>
  }

  const downloadPredictionReport = async () => {
    // Add loading message
    const loadingMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: '🔄 **Generating Fire Prediction Report...**\n\nPlease wait while I generate a comprehensive PDF report with ML predictions. This may take a few seconds.\n\n⏳ Analyzing fire risk data...\n⏳ Processing ML predictions...\n⏳ Creating authority-ready document...',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, loadingMessage])

    try {
      const response = await fetch('http://localhost:8000/api/chat/generate-prediction-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format: 'pdf'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate report')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `fire_prediction_report_${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Remove loading message and add success message
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessage.id)
        return [...filtered, {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '📄 **Fire Prediction Report Downloaded Successfully**\n\nA comprehensive fire prediction report has been generated and downloaded to your device. This PDF report contains:\n\n✅ ML-based fire risk predictions with live data\n✅ Risk level distribution analysis\n✅ Top high-risk locations with precise coordinates\n✅ Authority recommendations and action plans\n✅ Emergency response protocols\n\n**File:** fire_prediction_report_' + new Date().toISOString().split('T')[0] + '.pdf\n**Status:** Ready for distribution to authorities and emergency services\n\nYou can now send this report to local fire departments and emergency response teams.',
          timestamp: new Date().toISOString()
        }]
      })
    } catch (error) {
      console.error('Error downloading report:', error)
      // Remove loading message and add error message
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessage.id)
        return [...filtered, {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '❌ **Download Failed**\n\nSorry, I could not download the prediction report. This might be due to:\n\n• Backend server not responding\n• Network connectivity issues\n• PDF generation timeout\n\nPlease try again in a moment or check if the backend is running.',
          timestamp: new Date().toISOString()
        }]
      })
    }
  }

  const quickActions = [
    {
      label: 'Download Report',
      icon: FileText,
      action: downloadPredictionReport
    },
    {
      label: 'Punjab Predictions',
      icon: BarChart3,
      action: () => setInputMessage('Show me the top 5 highest probability predictions for Punjab')
    },
    {
      label: 'All Predictions',
      icon: Bot,
      action: () => setInputMessage('Show me the top 5 highest probability predictions for all northern india')
    }
  ]

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-50 group"
        >
          <MessageCircle className="w-6 h-6" />
          <div className="absolute -top-2 -left-2 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          
          {/* Tooltip */}
          <div className="absolute right-16 top-1/2 transform -translate-y-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            AI Fire Assistant
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white border border-gray-200 rounded-lg shadow-2xl z-50 flex flex-col">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">AI Fire Assistant</h3>
                <p className="text-xs text-blue-100">Fire monitoring & analysis</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-6 h-6 hover:bg-blue-500 rounded transition-colors flex items-center justify-center"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Actions */}
          <div className="p-3 border-b border-gray-100">
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.action}
                  className="flex items-center space-x-1 px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs transition-colors"
                >
                  <action.icon className="w-3 h-3" />
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.role === 'assistant' && (
                      <Bot className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-600" />
                    )}
                    {message.role === 'user' && (
                      <User className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-100" />
                    )}
                    <div className="text-sm leading-relaxed">
                      {message.role === 'assistant' ? formatMessage(message.content) : message.content}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 p-3 rounded-lg flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-100">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about fires, generate reports..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Press Enter to send • Ask about fire reports, statistics, or analysis
            </p>
          </div>
        </div>
      )}
    </>
  )
}