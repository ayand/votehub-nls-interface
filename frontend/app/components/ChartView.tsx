'use client'

import React, { useMemo } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, Legend } from 'recharts'
import ColorLegend from './ColorLegend'
import { Poll } from '../models'
import { normalizeChoice } from '../utils/pollUtils'

interface ChoiceData {
  displayName: string
  average: number
  color: string
}

interface ChartViewProps {
  choices: ChoiceData[]
  pollAmount: number
  polls: Poll[]
}

export default function ChartView({ choices, pollAmount, polls }: ChartViewProps) {
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

  // Prepare data for line chart with rolling average
  const lineChartData = useMemo(() => {
    // Sort polls by end_date
    const sortedPolls = [...polls].sort((a, b) =>
      new Date(a.end_date).getTime() - new Date(b.end_date).getTime()
    )

    // Create a map of choice -> array of {date, value} points
    // Use normalized choice names as keys to handle variations like "Trump, Jr." vs "Trump Jr"
    const choiceDataMap = new Map<string, Array<{date: Date, value: number, poll: Poll}>>()

    sortedPolls.forEach(poll => {
      poll.answers?.forEach(answer => {
        // Normalize the answer choice to match against normalized display names
        const normalizedAnswer = normalizeChoice(answer.choice)

        // Find the matching choice by normalizing both the displayName and answer.choice
        const choiceEntry = choices.find(c => normalizeChoice(c.displayName) === normalizedAnswer)

        if (choiceEntry) {
          // Use the displayName from choices as the key (this is already the shortest/cleanest version)
          if (!choiceDataMap.has(choiceEntry.displayName)) {
            choiceDataMap.set(choiceEntry.displayName, [])
          }
          choiceDataMap.get(choiceEntry.displayName)!.push({
            date: new Date(poll.end_date),
            value: answer.pct,
            poll: poll
          })
        }
      })
    })

    // Calculate 4-week rolling average for each choice
    const rollingAverages = new Map<string, Array<{date: number, value: number, rawValue?: number}>>()

    choiceDataMap.forEach((dataPoints, choiceName) => {
      const sortedPoints = dataPoints.sort((a, b) => a.date.getTime() - b.date.getTime())
      const averages: Array<{date: number, value: number, rawValue?: number}> = []

      sortedPoints.forEach((point, index) => {
        const fourWeeksAgo = new Date(point.date)
        fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28)

        // Get all points within 4 weeks
        const recentPoints = sortedPoints.filter(p =>
          p.date >= fourWeeksAgo && p.date <= point.date
        )

        // Calculate average
        const avg = recentPoints.reduce((sum, p) => sum + p.value, 0) / recentPoints.length

        averages.push({
          date: point.date.getTime(),
          value: parseFloat(avg.toFixed(1)),
          rawValue: point.value
        })
      })

      rollingAverages.set(choiceName, averages)
    })

    return { rawData: choiceDataMap, rollingAverages }
  }, [polls, choices])

  // Prepare scatter data (individual poll points)
  const scatterData = useMemo(() => {
    const result: Array<{choice: string, data: Array<{date: number, value: number}>}> = []

    lineChartData.rawData.forEach((dataPoints, choiceName) => {
      result.push({
        choice: choiceName,
        data: dataPoints.map(p => ({
          date: p.date.getTime(),
          value: p.value
        }))
      })
    })

    return result
  }, [lineChartData])

  // Prepare line data (rolling averages)
  const lineData = useMemo(() => {
    // Get all unique timestamps
    const allTimestamps = new Set<number>()
    lineChartData.rollingAverages.forEach(points => {
      points.forEach(p => allTimestamps.add(p.date))
    })

    const sortedTimestamps = Array.from(allTimestamps).sort((a, b) => a - b)

    // Create data points for each timestamp
    return sortedTimestamps.map(timestamp => {
      const dataPoint: any = { date: timestamp }

      choices.forEach(choice => {
        const rollingData = lineChartData.rollingAverages.get(choice.displayName)
        const point = rollingData?.find(p => p.date === timestamp)
        if (point) {
          dataPoint[choice.displayName] = point.value
        }
      })

      return dataPoint
    })
  }, [lineChartData, choices])

  return (
    <div style={{ marginBottom: '2rem' }}>
      {/* Color Legend */}
      <ColorLegend items={legendItems} />

      {/* Two-column layout */}
      <div style={{
        display: 'flex',
        gap: '2rem',
        flexWrap: 'wrap'
      }}>
        {/* Left column: Bar Chart */}
        <div style={{
          flex: '1 1 45%',
          minWidth: '400px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#1e40af',
            textAlign: 'center',
            marginBottom: '1rem'
          }}>
            Average Across {pollAmount} Polls
          </h2>

          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            padding: '2rem',
            flex: 1
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

        {/* Right column: Line Chart with scatter points */}
        <div style={{
          flex: '1 1 45%',
          minWidth: '400px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#1e40af',
            textAlign: 'center',
            marginBottom: '1rem'
          }}>
            Trend Over Time (4-Week Rolling Average)
          </h2>

          <div style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            padding: '2rem',
            flex: 1
          }}>
            <ResponsiveContainer width="100%" height={500}>
              <LineChart
                data={lineData}
                margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(timestamp) => {
                    const date = new Date(timestamp)
                    return `${date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`
                  }}
                  style={{
                    fontSize: '0.875rem',
                    fontFamily: 'system-ui, -apple-system, sans-serif'
                  }}
                />
                <YAxis
                  label={{
                    value: 'Support (%)',
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

                {/* Render scatter points for each choice */}
                {/* These are individual poll data points shown as semi-transparent dots */}
                {scatterData.map((scatter, idx) => {
                  const choice = choices.find(c => c.displayName === scatter.choice)
                  if (!choice) return null

                  return (
                    <Line
                      key={`scatter-${idx}`}
                      data={scatter.data}
                      type="monotone"
                      dataKey="value"
                      stroke="none"
                      dot={{
                        fill: choice.color,
                        r: 2,
                        fillOpacity: 0.4
                      }}
                      isAnimationActive={false}
                      connectNulls={false}
                    />
                  )
                })}

                {/* Render rolling average lines */}
                {/* These lines use choice.displayName as dataKey */}
                {choices.map((choice, idx) => (
                  <Line
                    key={`line-${idx}`}
                    type="monotone"
                    dataKey={choice.displayName}
                    stroke={choice.color}
                    strokeWidth={3}
                    dot={false}
                    connectNulls={true}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
