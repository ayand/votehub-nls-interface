import React, { useState, useEffect } from 'react'
import { PollsTableProps, Poll, Answer } from '../models';
import ChoicesSummary from './ChoicesSummary';
import { normalizeChoice, calculateChoicesWithColors } from '../utils/pollUtils';


export default function PollsTable({ polls, subject, pollType, colorMap }: PollsTableProps) {
  const [colorsLoaded, setColorsLoaded] = useState(false)

  // Calculate choices with colors using shared utility
  const choicesWithColors = calculateChoicesWithColors(polls, colorMap)

  // Calculate unique choices for this group of polls with normalization (for internal use)
  const choiceStats = new Map<string, { total: number; count: number; displayName: string; originalNames: string[] }>()
  polls.forEach((poll: Poll) => {
    poll.answers?.forEach((answer: Answer) => {
      const normalized = normalizeChoice(answer.choice)
      const stats = choiceStats.get(normalized) || { total: 0, count: 0, displayName: normalized, originalNames: [] }
      stats.total += answer.pct
      stats.count += 1
      stats.originalNames.push(answer.choice)
      // Use the shortest version as display name (usually the one without periods)
      if (answer.choice.length < stats.displayName.length) {
        stats.displayName = answer.choice
      }
      choiceStats.set(normalized, stats)
    })
  })

  // Sort choices by average percentage in descending order
  const uniqueChoices = Array.from(choiceStats.entries())
    .map(([normalized, stats]) => ({
      normalized,
      displayName: stats.displayName,
      average: stats.total / stats.count
    }))
    .sort((a, b) => b.average - a.average)

  // Set colors as loaded since they're passed as a prop
  useEffect(() => {
    setColorsLoaded(true)
  }, [colorMap])

  const getAnswerPct = (poll: Poll, normalizedChoice: string): number | null => {
    // Find answer by matching normalized choice name
    const answer = poll.answers?.find(a => normalizeChoice(a.choice) === normalizedChoice)
    return answer ? answer.pct : null
  }

  const getWinnerInfo = (poll: Poll): { winner: string; margin: number } | null => {
    if (!poll.answers || poll.answers.length === 0) return null

    const sorted = [...poll.answers].sort((a, b) => b.pct - a.pct)
    const winner = sorted[0]
    const margin = sorted.length > 1 ? winner.pct - sorted[1].pct : winner.pct

    // Use normalized name for winner
    const normalizedWinner = normalizeChoice(winner.choice)
    const displayName = choiceStats.get(normalizedWinner)?.displayName || winner.choice

    return { winner: displayName, margin }
  }

  const getWinnerColor = (poll: Poll, winnerChoice: string): string => {
    // First check if we have a color from the color map
    if (colorMap[winnerChoice]) {
      return colorMap[winnerChoice]
    }

    // Fallback to old logic if color map doesn't have it
    const pollTypeNormalized = poll.poll_type.toLowerCase()
    const winnerNormalized = normalizeChoice(winnerChoice).toLowerCase()

    if (pollTypeNormalized === 'approval' || pollTypeNormalized === 'favorability') {
      if (winnerNormalized === 'disapprove' || winnerNormalized === 'unfavorable') {
        return '#e08728' // Orange
      } else if (winnerNormalized === 'approve' || winnerNormalized === 'favorable') {
        return '#288544' // Green
      }
    } else if (pollTypeNormalized === 'generic-ballot') {
      if (winnerNormalized === 'dem') {
        return '#2853e0' // Blue
      } else if (winnerNormalized === 'rep') {
        return '#e02f28' // Red
      }
    }

    return '#000000' // Black for everything else
  }

  if (!colorsLoaded) {
    return (
      <div style={{
        marginBottom: '2rem',
        padding: '3rem',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        Loading colors...
      </div>
    )
  }

  return (
    <div style={{ marginBottom: '2rem' }}>
      <ChoicesSummary choices={choicesWithColors} pollAmount={polls.length} />
      <div style={{
        overflowX: 'auto',
        overflowY: 'auto',
        maxHeight: '70vh',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.875rem'
        }}>
          <thead style={{
            position: 'sticky',
            top: 0,
            backgroundColor: '#2563eb',
            color: 'white',
            zIndex: 10
          }}>
            <tr>
              <th style={headerStyle}>Pollster</th>
              <th style={headerStyle}>Start Date</th>
              <th style={headerStyle}>End Date</th>
              <th style={headerStyle}>Sample Size</th>
              <th style={headerStyle}>Result</th>
              {uniqueChoices.slice(0, 10).map(item => (
                <th 
                  key={item.normalized} 
                  style={{
                    ...headerStyle,
                    color: 'white'
                  }}
                >
                  {item.displayName} %
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {polls.map((poll, index) => (
              <tr
                key={poll.id}
                style={{
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f3f4f6',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#dbeafe'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = index % 2 === 0 ? '#ffffff' : '#f3f4f6'
                }}
              >
                <td style={cellStyle}>{poll.pollster}</td>
                <td style={cellStyle}>{poll.start_date}</td>
                <td style={cellStyle}>{poll.end_date}</td>
                <td style={cellStyle}>
                  {poll.sample_size !== null ? poll.sample_size.toLocaleString() : 'N/A'} ({poll.population})
                </td>
                <td style={cellStyle}>
                  {(() => {
                    const winnerInfo = getWinnerInfo(poll)
                    if (!winnerInfo) return '-'
                    if (winnerInfo.margin === 0) {
                      return (
                        <span style={{ fontWeight: '700', color: '#000000' }}>
                          Tied
                        </span>
                      )
                    }
                    const color = getWinnerColor(poll, winnerInfo.winner)
                    return (
                      <span style={{ fontWeight: '700', color }}>
                        {winnerInfo.winner} (+{winnerInfo.margin.toFixed(1)})
                      </span>
                    )
                  })()}
                </td>
                {uniqueChoices.slice(0, 10).map(item => {
                  const pct = getAnswerPct(poll, item.normalized)
                  const choiceColor = colorMap[item.displayName]
                  return (
                    <td
                      key={item.normalized}
                      style={{
                        ...cellStyle,
                        textAlign: 'center',
                        fontWeight: pct !== null ? '700' : 'normal',
                        color: pct !== null ? (choiceColor || '#000000') : '#9ca3af'
                      }}
                    >
                      {pct !== null ? `${pct}%` : '-'}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const headerStyle: React.CSSProperties = {
  padding: '1rem',
  textAlign: 'left',
  fontWeight: '600',
  fontSize: '0.875rem',
  letterSpacing: '0.05em',
  textTransform: 'uppercase',
  borderBottom: '2px solid #1e40af',
  whiteSpace: 'nowrap'
}

const cellStyle: React.CSSProperties = {
  padding: '0.75rem 1rem',
  borderBottom: '1px solid #e5e7eb',
  whiteSpace: 'nowrap'
}

