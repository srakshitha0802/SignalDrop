import { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">SignalDrop AI</h1>
            </div>
            <div className="flex space-x-8">
              <Link href="#problem-solution" className="text-gray-600 hover:text-gray-900 transition-colors">
                How It Works
              </Link>
              <Link href="/demo" className="text-gray-600 hover:text-gray-900 transition-colors">
                Live Demo
              </Link>
              <Link href="#architecture" className="text-gray-600 hover:text-gray-900 transition-colors">
                Architecture
              </Link>
              <Link href="#ethics" className="text-gray-600 hover:text-gray-900 transition-colors">
                Ethics
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Detect failures early by amplifying weak signals humans overlook.
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            SignalDrop AI is an early-warning GenAI system for education and institutions.
          </p>
          <Link href="/demo">
            <button className="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-primary-700 transition-colors">
              View Live Demo
            </button>
          </Link>
        </div>
      </section>

      {/* Problem → Solution */}
      <section id="problem-solution" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Problem */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">The Problem</h2>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <span className="text-red-500 mr-3">•</span>
                  <span className="text-gray-700">Failures don't happen suddenly</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-3">•</span>
                  <span className="text-gray-700">Early signals are fragmented</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-3">•</span>
                  <span className="text-gray-700">Dashboards react too late</span>
                </li>
              </ul>
            </div>

            {/* Solution */}
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">The Solution</h2>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <span className="text-green-500 mr-3">•</span>
                  <span className="text-gray-700">GenAI analyzes unstructured signals</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-3">•</span>
                  <span className="text-gray-700">Detects risk momentum over time</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-3">•</span>
                  <span className="text-gray-700">Explains why an alert is raised</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-semibold text-gray-900 text-center mb-12">Architecture & Credibility</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Architecture Diagram */}
            <div className="bg-gray-50 p-8 rounded-lg">
              <div className="space-y-4">
                <div className="bg-white p-4 rounded border border-gray-200">
                  <div className="text-sm font-medium text-gray-700">Data Sources</div>
                  <div className="text-xs text-gray-500 mt-1">LMS • Assignments • Messages • Attendance</div>
                </div>
                <div className="flex justify-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 text-xs">↓</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <div className="text-sm font-medium text-gray-700">Signal Processing</div>
                  <div className="text-xs text-gray-500 mt-1">Temporal Analysis • Multi-modal Fusion</div>
                </div>
                <div className="flex justify-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 text-xs">↓</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <div className="text-sm font-medium text-gray-700">GenAI Reasoning</div>
                  <div className="text-xs text-gray-500 mt-1">Causal Analysis • Narrative Extraction</div>
                </div>
                <div className="flex justify-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 text-xs">↓</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <div className="text-sm font-medium text-gray-700">Explainable Alerts</div>
                  <div className="text-xs text-gray-500 mt-1">Risk Scores • Natural Language Explanations</div>
                </div>
              </div>
            </div>

            {/* Credibility Points */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Technical Foundation</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">Multi-source signal ingestion</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">Temporal analysis with sliding windows</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">GenAI reasoning layer</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">Explainable outputs</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">Real-time processing capabilities</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-3">✓</span>
                  <span className="text-gray-700">Uncertainty quantification</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Ethics */}
      <section id="ethics" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-semibold text-gray-900 text-center mb-12">Ethics & Limits</h2>
          
          <div className="bg-white p-8 rounded-lg border border-gray-200">
            <div className="space-y-6">
              <div className="flex items-start">
                <div className="bg-primary-100 rounded-full p-2 mr-4">
                  <span className="text-primary-600 font-semibold">1</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">No Labels or Judgments</h3>
                  <p className="text-gray-600">This system does not label or judge students. It identifies patterns that may indicate risk.</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="bg-primary-100 rounded-full p-2 mr-4">
                  <span className="text-primary-600 font-semibold">2</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Risk Momentum, Not Outcomes</h3>
                  <p className="text-gray-600">Alerts indicate risk momentum over time, not predetermined outcomes.</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="bg-primary-100 rounded-full p-2 mr-4">
                  <span className="text-primary-600 font-semibold">3</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Human Intervention Required</h3>
                  <p className="text-gray-600">Human intervention is always required for interpretation and action.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600">
            <p>SignalDrop AI - Early Warning Risk Detection System</p>
            <p className="text-sm mt-2">Designed for educational institutions and research purposes.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
