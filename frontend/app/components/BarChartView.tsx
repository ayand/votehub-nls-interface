'use client'

import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import ColorLegend from './ColorLegend'

interface ChoiceData {
  displayName: string
  average: number
  color: string
}

interface BarChartViewProps {
  choices: ChoiceData[]
  pollAmount: number
}

export default function BarChartView({ choices, pollAmount }: BarChartViewProps) {
  if (choices.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        padding: '3rem',
        color: '#6b7280'
      }}>
        No data available for visualization
      </div>
    )
  }

  // Prepare data for the bar chart
  const chartData = choices.map(choice => ({
    name: choice.displayName,
    average: parseFloat(choice.average.toFixed(1)),
    color: choice.color
  }))

  // Prepare legend items
  const legendItems = choices.map(choice => ({
    displayName: choice.displayName,
    color: choice.color
  }))

  return (
    <div style={{ marginBottom: '2rem' }}>
      {/* Title */}
      <h2 style={{
        fontSize: '1.75rem',
        fontWeight: '600',
        color: '#1e40af',
        textAlign: 'center',
        marginBottom: '1.5rem',
        marginTop: '1rem'
      }}>
        Average Across {pollAmount} Polls
      </h2>

      {/* Color Legend */}
      <ColorLegend items={legendItems} />

      {/* Bar Chart */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        padding: '2rem'
      }}>
        <ResponsiveContainer width="100%" height={500}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 100 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={120}
              interval={0}
              style={{
                fontSize: '0.875rem',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}
            />
            <YAxis
              label={{
                value: 'Average Support (%)',
                angle: -90,
                position: 'insideLeft',
                style: {
                  fontSize: '0.875rem',
                  fontFamily: 'system-ui, -apple-system, sans-serif'
                }
              }}
              style={{
                fontSize: '0.875rem',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}
              labelStyle={{
                fontWeight: '600',
                marginBottom: '0.25rem'
              }}
              formatter={(value: number) => [`${value}%`, 'Average']}
            />
            <Bar dataKey="average" radius={[8, 8, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
