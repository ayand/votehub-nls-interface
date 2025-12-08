'use client'

import { useState } from 'react'
import PollsTable from './components/PollsTable'
import ChartView from './components/ChartView'
import LoadingSpinner from './components/LoadingSpinner'
import { Poll } from './models'
import { calculateChoicesWithColors } from './utils/pollUtils'

export default function Home() {
  const [query, setQuery] = useState<string>('')
  const [polls, setPolls] = useState<Poll[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [pollsGrouped, setPollsGrouped] = useState<Map<string, { subject: string; pollType: string; polls: Poll[]; colorMap: Record<string, string> }>>(new Map())
  const [activeTab, setActiveTab] = useState<string>('')
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('chart')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setPolls([])
    setPollsGrouped(new Map())

    try {
      const response = await fetch(
        `http://localhost:5001/api/polls?q=${encodeURIComponent(query)}`
      )
      if (!response.ok) {
        throw new Error('Failed to fetch polls')
      }
      const data = await response.json()

      // data is now an object with division keys mapping to { polls, color_map }
      // Example: { "Biden_approval": { polls: [...], color_map: {...} } }

      // Convert the divisions object to a grouped Map
      const grouped = new Map<string, { subject: string; pollType: string; polls: Poll[]; colorMap: Record<string, string> }>()
      let allPolls: Poll[] = []

      Object.entries(data).forEach(([divisionKey, divisionData]: [string, any]) => {
        // divisionKey format: "subject_poll_type"
        const [subject, ...pollTypeParts] = divisionKey.split('_')
        const pollType = pollTypeParts.join('-')

        // Sort polls by end_date in descending order
        const sortedPolls = divisionData.polls.sort((a: Poll, b: Poll) => {
          return new Date(b.end_date).getTime() - new Date(a.end_date).getTime()
        })

        const groupKey = `${subject}|${pollType}`
        grouped.set(groupKey, {
          subject: subject,
          pollType: pollType,
          polls: sortedPolls,
          colorMap: divisionData.color_map || {}
        })

        allPolls = allPolls.concat(sortedPolls)
      })

      setPolls(allPolls)
      setPollsGrouped(grouped)

      // Set the first group as the active tab
      const firstKey = Array.from(grouped.keys())[0]
      if (firstKey) {
        setActiveTab(firstKey)
      }
    } catch (err) {
      setError('Failed to fetch polls. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      maxWidth: '100%',
      overflowX: 'auto'
    }}>
      <div
        style={{
          backgroundColor: '#e0f2fe', // light blue
          padding: '1.5rem 1rem',
          borderRadius: '12px',
          marginBottom: '2rem',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '2rem',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <h1
          style={{
            fontSize: '2rem',
            color: '#1e40af',
            margin: 0,
            flex: '0 0 auto',
            whiteSpace: 'nowrap'
          }}
        >
          VoteHub Poll Search
        </h1>

        <form onSubmit={handleSearch} style={{
          flex: '1 1 350px',
          minWidth: '250px',
          maxWidth: '700px',
        }}>
          <div
            style={{
              display: 'flex',
              gap: '1rem',
              alignItems: 'center',
              width: '100%',
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your poll query (e.g., 'Biden approval ratings in the last month')"
              style={{
                flex: 1,
                padding: '0.5rem 0.75rem',
                fontSize: '1rem',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                outline: 'none',
                transition: 'border-color 0.2s',
                minWidth: 0
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '0.5rem 1.5rem',
                fontSize: '1rem',
                fontWeight: '600',
                color: 'white',
                backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#2563eb'
              }}
              onMouseLeave={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#3b82f6'
              }}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#fee2e2',
          color: '#991b1b',
          borderRadius: '8px',
          marginBottom: '1rem'
        }}>
          {error}
        </div>
      )}

      {loading && <LoadingSpinner />}

      {!loading && polls.length > 0 && (
        <div>
          {/* Tab Navigation */}
          <div style={{
            display: 'flex',
            gap: '0.5rem',
            marginBottom: '1.5rem',
            borderBottom: '2px solid #e5e7eb',
            overflowX: 'auto',
            flexWrap: 'wrap'
          }}>
            {Array.from(pollsGrouped.entries()).map(([groupKey, group]) => {
              const title = group.subject ? `${group.subject} - ${group.pollType.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}` : group.pollType.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
              return <button
                key={groupKey}
                onClick={() => setActiveTab(groupKey)}
                style={{
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.95rem',
                  fontWeight: activeTab === groupKey ? '600' : '500',
                  color: activeTab === groupKey ? '#2563eb' : '#6b7280',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === groupKey ? '3px solid #2563eb' : '3px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  whiteSpace: 'nowrap',
                  marginBottom: '-2px'
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== groupKey) {
                    e.currentTarget.style.color = '#3b82f6'
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== groupKey) {
                    e.currentTarget.style.color = '#6b7280'
                  }
                }}
              >
                {title}
              </button>
            })}
          </div>

          {/* View Mode Toggle */}
          {activeTab && pollsGrouped.has(activeTab) && (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '0.5rem',
              marginBottom: '1.5rem'
            }}>
              <button
                onClick={() => setViewMode('chart')}
                style={{
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.95rem',
                  fontWeight: viewMode === 'chart' ? '600' : '500',
                  color: viewMode === 'chart' ? '#ffffff' : '#6b7280',
                  backgroundColor: viewMode === 'chart' ? '#2563eb' : '#ffffff',
                  border: `2px solid ${viewMode === 'chart' ? '#2563eb' : '#e5e7eb'}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (viewMode !== 'chart') {
                    e.currentTarget.style.borderColor = '#3b82f6'
                    e.currentTarget.style.color = '#3b82f6'
                  }
                }}
                onMouseLeave={(e) => {
                  if (viewMode !== 'chart') {
                    e.currentTarget.style.borderColor = '#e5e7eb'
                    e.currentTarget.style.color = '#6b7280'
                  }
                }}
              >
                📈 Chart View
              </button>
              <button
                onClick={() => setViewMode('table')}
                style={{
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.95rem',
                  fontWeight: viewMode === 'table' ? '600' : '500',
                  color: viewMode === 'table' ? '#ffffff' : '#6b7280',
                  backgroundColor: viewMode === 'table' ? '#2563eb' : '#ffffff',
                  border: `2px solid ${viewMode === 'table' ? '#2563eb' : '#e5e7eb'}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (viewMode !== 'table') {
                    e.currentTarget.style.borderColor = '#3b82f6'
                    e.currentTarget.style.color = '#3b82f6'
                  }
                }}
                onMouseLeave={(e) => {
                  if (viewMode !== 'table') {
                    e.currentTarget.style.borderColor = '#e5e7eb'
                    e.currentTarget.style.color = '#6b7280'
                  }
                }}
              >
                📊 Table View
              </button>
            </div>
          )}
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '700', 
            color: '#1e40af', 
            textAlign: 'center', 
            marginTop: '1.5rem',
            marginBottom: '1.5rem'
          }}>
            {pollsGrouped.get(activeTab)!.subject && (
              <>
                {pollsGrouped.get(activeTab)!.subject}
                {' - '}
              </>
            )}
            {pollsGrouped.get(activeTab)!.pollType
              .split('-')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ')}
          </h2>

          {/* Active Tab Content */}
          {activeTab && pollsGrouped.has(activeTab) && (
            <>
              {viewMode === 'table' ? (
                <PollsTable
                  polls={pollsGrouped.get(activeTab)!.polls}
                  subject={pollsGrouped.get(activeTab)!.subject}
                  pollType={pollsGrouped.get(activeTab)!.pollType}
                  colorMap={pollsGrouped.get(activeTab)!.colorMap}
                />
              ) : (
                <ChartView
                  choices={calculateChoicesWithColors(
                    pollsGrouped.get(activeTab)!.polls,
                    pollsGrouped.get(activeTab)!.colorMap
                  )}
                  pollAmount={pollsGrouped.get(activeTab)!.polls.length}
                  polls={pollsGrouped.get(activeTab)!.polls}
                />
              )}
            </>
          )}
        </div>
      )}

      {!loading && polls.length === 0 && query && !error && (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          color: '#6b7280'
        }}>
          No polls found for your query. Try a different search.
        </div>
      )}
    </main>
  )
}
