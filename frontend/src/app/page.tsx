'use client'

import { Flame, TrendingUp, BookOpen, MessageCircle } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-ash-light to-gray-100">
      <div className="container mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-charcoal mb-4">
            stubble burning detection system
          </h1>
          <p className="text-xl text-smoke-gray max-w-3xl mx-auto mb-6">
            advanced fire detection and prediction system for northern india using satellite data and machine learning
          </p>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-3">
              <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">!</span>
              </div>
              <h2 className="text-xl font-semibold text-red-800">stubble burning is illegal</h2>
            </div>
            <p className="text-red-700 text-base">
              burning crop residue is prohibited by law across northern india. violators face heavy fines and legal action.
              this detection system helps authorities identify and prevent illegal burning activities to protect public health and environment.
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Link href="/fire-detection" className="group">
            <div className="stats-card group-hover:shadow-lg transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-fire-red/10 rounded-lg flex items-center justify-center mr-4">
                  <Flame className="w-6 h-6 text-fire-red" />
                </div>
                <h3 className="text-xl font-semibold">fire detection</h3>
              </div>
              <p className="text-smoke-gray text-base">
                real-time monitoring and detection of illegal stubble burning for law enforcement and regulatory authorities
              </p>
            </div>
          </Link>

          <Link href="/fire-prediction" className="group">
            <div className="stats-card group-hover:shadow-lg transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-fire-orange/10 rounded-lg flex items-center justify-center mr-4">
                  <TrendingUp className="w-6 h-6 text-fire-orange" />
                </div>
                <h3 className="text-xl font-semibold">fire prediction</h3>
              </div>
              <p className="text-smoke-gray text-base">
                predictive analytics to help authorities anticipate and prevent illegal stubble burning activities
              </p>
            </div>
          </Link>

          <Link href="/awareness" className="group">
            <div className="stats-card group-hover:shadow-lg transition-all duration-300">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-fire-yellow/10 rounded-lg flex items-center justify-center mr-4">
                  <BookOpen className="w-6 h-6 text-fire-yellow" />
                </div>
                <h3 className="text-xl font-semibold">awareness</h3>
              </div>
              <p className="text-smoke-gray text-base">
                educational resources about health impacts and legal consequences of stubble burning
              </p>
            </div>
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-semibold mb-6 text-center">about the system</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-3">data sources</h3>
              <ul className="space-y-2 text-smoke-gray">
                <li>• nasa firms modis thermal anomalies</li>
                <li>• viirs active fire detections</li>
                <li>• weather and meteorological data</li>
                <li>• agricultural practice patterns</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3">capabilities</h3>
              <ul className="space-y-2 text-smoke-gray">
                <li>• real-time fire monitoring</li>
                <li>• predictive risk modeling</li>
                <li>• regional pattern analysis</li>
                <li>• educational content delivery</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <MessageCircle className="w-5 h-5 text-blue-600 mr-2" />
                ai fire assistant
              </h3>
              <ul className="space-y-2 text-smoke-gray">
                <li>• future fire prediction analysis</li>
                <li>• downloadable authority reports</li>
                <li>• statistical fire data insights</li>
                <li>• automated severity calculations</li>
                <li>• intelligent query processing</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}