'use client'

import { useState } from 'react'
import { 
  Leaf, 
  Recycle, 
  Heart, 
  Users, 
  BookOpen, 
  AlertCircle,
  TrendingDown,
  TrendingUp,
  DollarSign,
  Thermometer,
  Wind,
  Activity,
  Award,
  FileText,
  Satellite,
  BarChart3
} from 'lucide-react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts'

export default function Awareness() {
  const [selectedTab, setSelectedTab] = useState('overview')

  const tabs = [
    { id: 'overview', label: 'overview' },
    { id: 'impacts', label: 'environmental impact' },
    { id: 'health', label: 'health effects' },
    { id: 'climate', label: 'climate change' },
    { id: 'solutions', label: 'sustainable solutions' },
    { id: 'success', label: 'success stories' },
    { id: 'policies', label: 'government policies' }
  ]

  // Sample data for charts
  const airQualityData = [
    { month: 'oct', normal: 120, burning: 420 },
    { month: 'nov', normal: 135, burning: 480 },
    { month: 'dec', normal: 150, burning: 380 },
    { month: 'jan', normal: 140, burning: 320 },
    { month: 'feb', normal: 125, burning: 250 }
  ]

  const economicImpactData = [
    { category: 'healthcare costs', amount: 2800 },
    { category: 'agricultural loss', amount: 3200 },
    { category: 'tourism impact', amount: 1500 },
    { category: 'infrastructure damage', amount: 1200 },
    { category: 'business losses', amount: 2100 },
    { category: 'cleanup costs', amount: 900 }
  ]

  const cropResidueData = [
    { state: 'punjab', residue: 20.2, burned: 16.8 },
    { state: 'haryana', residue: 15.6, burned: 12.4 },
    { state: 'uttar pradesh', residue: 22.8, burned: 15.2 },
    { state: 'rajasthan', residue: 8.4, burned: 5.6 }
  ]

  const healthImpactData = [
    { name: 'respiratory diseases', value: 35, color: '#FF385C' },
    { name: 'cardiovascular issues', value: 28, color: '#FF7A00' },
    { name: 'eye irritation', value: 22, color: '#FFD60A' },
    { name: 'skin problems', value: 15, color: '#9CA3AF' }
  ]

  const emissionTrendsData = [
    { year: '2019', co2: 28.5, pm25: 12.8, nox: 8.4 },
    { year: '2020', co2: 32.1, pm25: 14.2, nox: 9.1 },
    { year: '2021', co2: 35.8, pm25: 16.5, nox: 10.2 },
    { year: '2022', co2: 33.2, pm25: 15.1, nox: 9.8 },
    { year: '2023', co2: 30.9, pm25: 13.9, nox: 9.2 },
    { year: '2024', co2: 29.1, pm25: 12.5, nox: 8.6 }
  ]

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-fire-red to-fire-orange rounded-lg p-8 text-white">
        <div className="flex items-center mb-4">
          <AlertCircle className="w-8 h-8 mr-3" />
          <h2 className="text-2xl font-semibold">the stubble burning crisis</h2>
        </div>
        <p className="text-xl opacity-90 mb-4">
          stubble burning is illegal across northern india with severe penalties for violators.
          despite this, millions of tonnes of crop residue are still burned annually.
        </p>
        <p className="text-lg opacity-90 mb-6">
          this detection system helps authorities identify illegal burning activities and enforce regulations
          to protect public health and the environment.
        </p>
        
        <div className="grid md:grid-cols-4 gap-6">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">23M</div>
            <div className="text-sm opacity-90">tonnes burned annually</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">50M+</div>
            <div className="text-sm opacity-90">people affected</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">40-50%</div>
            <div className="text-sm opacity-90">air pollution increase</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">₹15k</div>
            <div className="text-sm opacity-90">maximum fine per violation</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="stats-card">
          <div className="flex items-center mb-4">
            <Wind className="w-6 h-6 text-fire-red mr-3" />
            <h3 className="text-lg font-semibold">air quality impact</h3>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={airQualityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="normal" fill="#9CA3AF" name="normal aqi" />
                <Bar dataKey="burning" fill="#FF385C" name="during burning" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-center mb-4">
            <Activity className="w-6 h-6 text-fire-orange mr-3" />
            <h3 className="text-lg font-semibold">health impact distribution</h3>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={healthImpactData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  label={({ name, value }) => `${value}%`}
                >
                  {healthImpactData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-center mb-4">
            <Thermometer className="w-6 h-6 text-fire-yellow mr-3" />
            <h3 className="text-lg font-semibold">emission trends</h3>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={emissionTrendsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="co2" stroke="#FF385C" name="co2 (mt)" />
                <Line type="monotone" dataKey="pm25" stroke="#FF7A00" name="pm2.5 (kt)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )

  const renderImpacts = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">environmental devastation</h2>
        <p className="text-smoke-gray">comprehensive analysis of environmental damage caused by stubble burning</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">air quality degradation</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={airQualityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="normal" stackId="1" stroke="#9CA3AF" fill="#9CA3AF" fillOpacity={0.6} />
                <Area type="monotone" dataKey="burning" stackId="1" stroke="#FF385C" fill="#FF385C" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-sm space-y-2">
            <div>• aqi levels increase by 250-400% during burning season</div>
            <div>• pm2.5 concentrations exceed safe limits by 10-15 times</div>
            <div>• visibility reduced to less than 50 meters in affected areas</div>
          </div>
        </div>

        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">soil degradation impacts</h3>
          <div className="space-y-4">
            <div className="bg-fire-red/10 p-4 rounded-lg">
              <div className="font-semibold text-fire-red mb-2">organic matter loss</div>
              <div className="text-sm">burning destroys 25-30% of soil organic carbon, reducing fertility</div>
            </div>
            <div className="bg-fire-orange/10 p-4 rounded-lg">
              <div className="font-semibold text-fire-orange mb-2">microbial ecosystem</div>
              <div className="text-sm">eliminates beneficial bacteria and fungi essential for nutrient cycling</div>
            </div>
            <div className="bg-fire-yellow/10 p-4 rounded-lg">
              <div className="font-semibold text-yellow-600 mb-2">nutrient depletion</div>
              <div className="text-sm">loss of nitrogen, phosphorus, and potassium reduces crop yields</div>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-card">
        <h3 className="text-lg font-semibold mb-4">crop residue burning by state</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cropResidueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="state" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="residue" fill="#9CA3AF" name="total residue (mt)" />
              <Bar dataKey="burned" fill="#FF385C" name="burned (mt)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )

  const renderHealth = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">public health emergency</h2>
        <p className="text-smoke-gray">serious health consequences affecting millions across northern india</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">immediate health effects</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-fire-red rounded-full mt-2"></div>
              <div>
                <div className="font-semibold text-sm">respiratory complications</div>
                <div className="text-sm text-smoke-gray">asthma attacks increase by 40%, bronchitis cases double</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-fire-orange rounded-full mt-2"></div>
              <div>
                <div className="font-semibold text-sm">cardiovascular stress</div>
                <div className="text-sm text-smoke-gray">heart attacks increase by 25% in affected regions</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-fire-yellow rounded-full mt-2"></div>
              <div>
                <div className="font-semibold text-sm">eye and skin irritation</div>
                <div className="text-sm text-smoke-gray">conjunctivitis and dermatitis cases surge</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
              <div>
                <div className="font-semibold text-sm">child health impact</div>
                <div className="text-sm text-smoke-gray">stunted lung development, increased school absences</div>
              </div>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">vulnerable populations</h3>
          <div className="space-y-4">
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <div className="font-semibold text-red-800 mb-2">children under 5</div>
              <div className="text-sm text-red-700">3x higher risk of respiratory infections, developmental delays</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <div className="font-semibold text-orange-800 mb-2">elderly (65+)</div>
              <div className="text-sm text-orange-700">increased mortality risk, chronic disease exacerbation</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <div className="font-semibold text-yellow-800 mb-2">pregnant women</div>
              <div className="text-sm text-yellow-700">preterm births, low birth weight babies</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="stats-card text-center">
          <Activity className="w-8 h-8 text-fire-red mx-auto mb-3" />
          <div className="text-2xl font-bold text-fire-red">2.5M+</div>
          <div className="text-sm text-smoke-gray">annual respiratory cases</div>
        </div>
        <div className="stats-card text-center">
          <Heart className="w-8 h-8 text-fire-orange mx-auto mb-3" />
          <div className="text-2xl font-bold text-fire-orange">180k+</div>
          <div className="text-sm text-smoke-gray">cardiovascular admissions</div>
        </div>
        <div className="stats-card text-center">
          <TrendingUp className="w-8 h-8 text-red-600 mx-auto mb-3" />
          <div className="text-2xl font-bold text-red-600">15%</div>
          <div className="text-sm text-smoke-gray">mortality increase</div>
        </div>
      </div>
    </div>
  )

  const renderEconomics = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">economic devastation</h2>
        <p className="text-smoke-gray">financial impact across sectors and communities</p>
      </div>

      <div className="stats-card">
        <h3 className="text-lg font-semibold mb-4">annual economic losses (₹ crores)</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={economicImpactData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="category" type="category" width={120} />
              <Tooltip />
              <Bar dataKey="amount" fill="#FF385C" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="stats-card">
          <DollarSign className="w-6 h-6 text-fire-red mb-3" />
          <h3 className="text-lg font-semibold mb-2">healthcare burden</h3>
          <div className="space-y-2 text-xs">
            <div>• emergency room visits increase 300%</div>
            <div>• chronic treatment costs rise 45%</div>
            <div>• insurance claims surge during season</div>
            <div>• lost productivity due to illness</div>
          </div>
        </div>

        <div className="stats-card">
          <TrendingDown className="w-6 h-6 text-fire-orange mb-3" />
          <h3 className="text-lg font-semibold mb-2">agricultural losses</h3>
          <div className="space-y-2 text-xs">
            <div>• soil fertility degradation</div>
            <div>• reduced crop yields next season</div>
            <div>• increased fertilizer requirements</div>
            <div>• long-term land value decline</div>
          </div>
        </div>

        <div className="stats-card">
          <Recycle className="w-6 h-6 text-fire-yellow mb-3" />
          <h3 className="text-lg font-semibold mb-2">opportunity costs</h3>
          <div className="space-y-2 text-xs">
            <div>• lost biomass revenue potential</div>
            <div>• missed biofuel opportunities</div>
            <div>• unused paper industry feedstock</div>
            <div>• foregone carbon credits</div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderClimate = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">climate change acceleration</h2>
        <p className="text-smoke-gray">contribution to global warming and climate instability</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">greenhouse gas emissions</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={emissionTrendsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="co2" stroke="#FF385C" strokeWidth={3} name="co2 (million tonnes)" />
                <Line type="monotone" dataKey="pm25" stroke="#FF7A00" strokeWidth={2} name="pm2.5 (thousand tonnes)" />
                <Line type="monotone" dataKey="nox" stroke="#FFD60A" strokeWidth={2} name="nox (thousand tonnes)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stats-card">
          <h3 className="text-lg font-semibold mb-4">carbon footprint breakdown</h3>
          <div className="space-y-4">
            <div className="bg-fire-red/10 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-fire-red">co2 emissions</span>
                <span className="text-sm">29.1 mt/year</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-fire-red h-2 rounded-full" style={{width: '85%'}}></div>
              </div>
            </div>
            <div className="bg-fire-orange/10 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-fire-orange">methane (ch4)</span>
                <span className="text-sm">0.8 mt/year</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-fire-orange h-2 rounded-full" style={{width: '40%'}}></div>
              </div>
            </div>
            <div className="bg-fire-yellow/10 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-yellow-600">nitrous oxide (n2o)</span>
                <span className="text-sm">0.3 mt/year</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{width: '25%'}}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
        <h3 className="text-lg font-semibold mb-4">global climate impact</h3>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">4.2%</div>
            <div className="text-xs opacity-90">of india's total ghg emissions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">0.15°c</div>
            <div className="text-xs opacity-90">contribution to regional warming</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">45 days</div>
            <div className="text-xs opacity-90">atmospheric residence time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">2000km</div>
            <div className="text-xs opacity-90">pollution transport range</div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderSolutions = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">sustainable alternatives</h2>
        <p className="text-smoke-gray">proven methods to manage crop residue without burning</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="stats-card">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <Recycle className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold">happy seeder technology</h3>
          </div>
          <p className="text-xs text-smoke-gray mb-4">
            direct seeding equipment that cuts and lifts rice straw, sows wheat seed, 
            and deposits straw over the sown area as mulch
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>cost reduction</span>
              <span className="font-semibold text-green-600">20-25%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>time savings</span>
              <span className="font-semibold text-green-600">40-50%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>yield improvement</span>
              <span className="font-semibold text-green-600">8-12%</span>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Leaf className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold">biomass utilization</h3>
          </div>
          <p className="text-xs text-smoke-gray mb-4">
            convert crop residue into useful products like biofuel, paper, 
            building materials, and industrial feedstock
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>additional income</span>
              <span className="font-semibold text-blue-600">₹2000-3000/acre</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>job creation</span>
              <span className="font-semibold text-blue-600">50k+ jobs</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>market value</span>
              <span className="font-semibold text-blue-600">₹8000 crores</span>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
              <Heart className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold">in-situ decomposition</h3>
          </div>
          <p className="text-xs text-smoke-gray mb-4">
            use of microbial solutions to decompose stubble in the field naturally, 
            enriching soil nutrients and maintaining ecosystem balance
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>soil organic carbon</span>
              <span className="font-semibold text-purple-600">+15-20%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>nutrient availability</span>
              <span className="font-semibold text-purple-600">+25-30%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>water retention</span>
              <span className="font-semibold text-purple-600">+18-22%</span>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
              <Users className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold">cooperative farming</h3>
          </div>
          <p className="text-xs text-smoke-gray mb-4">
            community-based approach to share equipment and resources for stubble management, 
            making sustainable practices accessible to small farmers
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>equipment cost sharing</span>
              <span className="font-semibold text-orange-600">60-70% reduction</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>farmer participation</span>
              <span className="font-semibold text-orange-600">1.2m+ farmers</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>operational efficiency</span>
              <span className="font-semibold text-orange-600">+35-40%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderSuccess = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">success stories</h2>
        <p className="text-smoke-gray">real-world examples of successful stubble management initiatives</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="stats-card">
          <div className="flex items-start space-x-4 mb-4">
            <Award className="w-8 h-8 text-green-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold">punjab's turnaround story</h3>
              <p className="text-xs text-smoke-gray">from 70% burning to 25% in 3 years</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 text-xs mb-1">machinery subsidy program</div>
              <div className="text-xs text-green-700">50-80% subsidy on happy seeder, super seeder, and balers</div>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 text-xs mb-1">farmer training initiatives</div>
              <div className="text-xs text-blue-700">trained 45,000+ farmers on sustainable practices</div>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 text-xs mb-1">enforcement measures</div>
              <div className="text-xs text-purple-700">satellite monitoring, fines, and positive reinforcement</div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-green-600">45%</div>
              <div className="text-xs text-smoke-gray">burning reduction</div>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-blue-600">12k</div>
              <div className="text-xs text-smoke-gray">machines distributed</div>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-purple-600">₹600cr</div>
              <div className="text-xs text-smoke-gray">investment made</div>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <div className="flex items-start space-x-4 mb-4">
            <Leaf className="w-8 h-8 text-blue-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold">haryana's biomass revolution</h3>
              <p className="text-xs text-smoke-gray">creating value from waste residue</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 text-xs mb-1">biomass power plants</div>
              <div className="text-xs text-blue-700">15 plants generating 150 mw electricity from crop residue</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 text-xs mb-1">pellet manufacturing</div>
              <div className="text-xs text-green-700">200+ units producing biomass pellets for export</div>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg border border-orange-200">
              <div className="font-semibold text-orange-800 text-xs mb-1">paper industry integration</div>
              <div className="text-xs text-orange-700">partnerships with 8 major paper mills</div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-blue-600">₹800</div>
              <div className="text-xs text-smoke-gray">per tonne price</div>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-green-600">8.5mt</div>
              <div className="text-xs text-smoke-gray">residue utilized</div>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <div className="text-lg font-bold text-orange-600">25k</div>
              <div className="text-xs text-smoke-gray">jobs created</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
        <h3 className="text-lg font-semibold mb-4">community impact highlights</h3>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">2.3M</div>
            <div className="text-xs opacity-90">farmers adopting alternatives</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">15.6M</div>
            <div className="text-xs opacity-90">tonnes residue managed sustainably</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">₹4800</div>
            <div className="text-xs opacity-90">average additional income per farmer</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">35%</div>
            <div className="text-xs opacity-90">reduction in regional air pollution</div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderPolicies = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-charcoal mb-2">government policies & regulations</h2>
        <p className="text-smoke-gray">comprehensive policy framework and support mechanisms</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="stats-card">
          <FileText className="w-6 h-6 text-fire-red mb-3" />
          <h3 className="text-lg font-semibold mb-4">central government schemes</h3>
          <div className="space-y-3">
            <div className="border-l-4 border-fire-red pl-4">
              <div className="font-semibold text-xs">crop residue management scheme</div>
              <div className="text-xs text-smoke-gray mt-1">₹2653 crores allocated for machinery subsidy</div>
            </div>
            <div className="border-l-4 border-fire-orange pl-4">
              <div className="font-semibold text-xs">pradhan mantri krishi sinchai yojana</div>
              <div className="text-xs text-smoke-gray mt-1">promoting zero tillage and conservation agriculture</div>
            </div>
            <div className="border-l-4 border-fire-yellow pl-4">
              <div className="font-semibold text-xs">national mission for sustainable agriculture</div>
              <div className="text-xs text-smoke-gray mt-1">climate resilient practices and soil health management</div>
            </div>
          </div>
        </div>

        <div className="stats-card">
          <BarChart3 className="w-6 h-6 text-blue-600 mb-3" />
          <h3 className="text-lg font-semibold mb-4">state-level initiatives</h3>
          <div className="space-y-3">
            <div className="border-l-4 border-blue-600 pl-4">
              <div className="font-semibold text-xs">punjab pollution control board</div>
              <div className="text-xs text-smoke-gray mt-1">real-time monitoring and enforcement mechanisms</div>
            </div>
            <div className="border-l-4 border-green-600 pl-4">
              <div className="font-semibold text-xs">haryana residue management policy</div>
              <div className="text-xs text-smoke-gray mt-1">incentives for biomass utilization and penalties for burning</div>
            </div>
            <div className="border-l-4 border-purple-600 pl-4">
              <div className="font-semibold text-xs">uttar pradesh clean air initiative</div>
              <div className="text-xs text-smoke-gray mt-1">integrated approach with ngt guidelines compliance</div>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-card">
        <h3 className="text-lg font-semibold mb-4">subsidy structure breakdown</h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Recycle className="w-8 h-8 text-green-600" />
            </div>
            <div className="text-lg font-bold text-green-600">50-80%</div>
            <div className="text-xs text-smoke-gray">subsidy on machinery</div>
            <div className="text-xs text-smoke-gray mt-1">happy seeder, super seeder, balers</div>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <DollarSign className="w-8 h-8 text-blue-600" />
            </div>
            <div className="text-lg font-bold text-blue-600">₹1000</div>
            <div className="text-xs text-smoke-gray">incentive per acre</div>
            <div className="text-xs text-smoke-gray mt-1">for adopting alternatives</div>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Users className="w-8 h-8 text-purple-600" />
            </div>
            <div className="text-lg font-bold text-purple-600">100%</div>
            <div className="text-xs text-smoke-gray">funding for fpos</div>
            <div className="text-xs text-smoke-gray mt-1">farmer producer organizations</div>
          </div>
        </div>
      </div>

      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-800 mb-4">enforcement measures</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-xs mb-2">monitoring systems</h4>
            <ul className="space-y-1 text-xs text-red-700">
              <li>• satellite-based real-time fire detection</li>
              <li>• drone surveillance in hotspot areas</li>
              <li>• mobile app for citizen reporting</li>
              <li>• gps-enabled field monitoring</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-xs mb-2">penalty structure</h4>
            <ul className="space-y-1 text-xs text-red-700">
              <li>• ₹2500 fine for plots up to 2 acres</li>
              <li>• ₹5000 fine for plots 2-5 acres</li>
              <li>• ₹15000 fine for plots above 5 acres</li>
              <li>• red entry in land records</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <Satellite className="w-6 h-6 text-green-600 mb-3" />
        <h3 className="text-lg font-semibold text-green-800 mb-4">digital initiatives</h3>
        <div className="grid md:grid-cols-4 gap-4">
          <div>
            <div className="font-semibold text-xs text-green-800">crop residue app</div>
            <div className="text-xs text-green-700 mt-1">machinery booking and tracking</div>
          </div>
          <div>
            <div className="font-semibold text-xs text-green-800">satellite monitoring</div>
            <div className="text-xs text-green-700 mt-1">real-time fire detection alerts</div>
          </div>
          <div>
            <div className="font-semibold text-xs text-green-800">farmer portal</div>
            <div className="text-xs text-green-700 mt-1">subsidy application and tracking</div>
          </div>
          <div>
            <div className="font-semibold text-xs text-green-800">data analytics</div>
            <div className="text-xs text-green-700 mt-1">predictive modeling for interventions</div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (selectedTab) {
      case 'overview': return renderOverview()
      case 'impacts': return renderImpacts()
      case 'health': return renderHealth()
      case 'climate': return renderClimate()
      case 'solutions': return renderSolutions()
      case 'success': return renderSuccess()
      case 'policies': return renderPolicies()
      default: return renderOverview()
    }
  }

  return (
    <div className="min-h-screen bg-ash-light">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-charcoal mb-2">stubble burning impact education</h1>
          <p className="text-smoke-gray">comprehensive analysis of environmental, health, and economic impacts</p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-8">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`px-4 py-2 rounded-lg text-xs transition-colors duration-200 ${
                  selectedTab === tab.id
                    ? 'bg-fire-red text-white'
                    : 'bg-gray-100 text-smoke-gray hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="animate-fade-in">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}