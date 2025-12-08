'use client'

import React, { useState, useEffect } from 'react'

const LOADING_MESSAGES = [
  "Counting the ballots...",
  "Polling the pollsters...",
  "Calculating the margins...",
  "Consulting the pundits...",
  "Analyzing the demographics...",
  "Reading the tea leaves...",
  "Crunching the numbers...",
  "Surveying the landscape...",
  "Measuring public opinion...",
  "Tallying the votes...",
  "Forecasting the results...",
  "Weighing the evidence...",
  "Parsing the data...",
  "Gauging the sentiment...",
  "Tracking the trends...",
  "Sampling the electorate...",
  "Computing the averages...",
  "Predicting the outcome...",
  "Monitoring the race..."
]

interface LoadingSpinnerProps {
  message?: string
}

export default function LoadingSpinner({ message }: LoadingSpinnerProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0)
  const [colorIndex, setColorIndex] = useState(0)

  // Cycle through messages every 2 seconds
  useEffect(() => {
    const messageInterval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length)
    }, 2000)

    return () => clearInterval(messageInterval)
  }, [])

  // Alternate colors every 1 second
  useEffect(() => {
    const colorInterval = setInterval(() => {
      setColorIndex((prev) => (prev + 1) % 2)
    }, 1000)

    return () => clearInterval(colorInterval)
  }, [])

  const currentColor = colorIndex === 0 ? '#e02f28' : '#2563eb' // Red and Blue
  const displayMessage = message || LOADING_MESSAGES[currentMessageIndex]

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem',
        minHeight: '300px'
      }}
    >
      {/* Rotating Circle Container */}
      <div
        style={{
          position: 'relative',
          width: '120px',
          height: '120px',
          marginBottom: '2rem'
        }}
      >
        {/* Rotating Circle Border */}
        <svg
          width="120"
          height="120"
          viewBox="0 0 120 120"
          style={{
            transform: 'rotate(-90deg)',
            animation: 'spin 2s linear infinite'
          }}
        >
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke={currentColor}
            strokeWidth="8"
            strokeDasharray="339.292" // Circumference of circle (2 * π * r)
            strokeDashoffset="84.823" // 1/4 of circumference for 3/4 circle
            strokeLinecap="round"
            style={{
              transition: 'stroke 0.5s ease-in-out'
            }}
          />
        </svg>

        {/* Center Icon - Vote/Check */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '3rem',
            transition: 'color 0.5s ease-in-out',
            color: currentColor
          }}
        >
          🗳️
        </div>
      </div>

      {/* Loading Message */}
      <div
        style={{
          fontSize: '1.25rem',
          fontWeight: '600',
          color: '#1e40af',
          textAlign: 'center',
          minHeight: '2rem',
          animation: 'fadeIn 0.5s ease-in-out'
        }}
      >
        {displayMessage}
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes spin {
          0% {
            transform: rotate(-90deg);
          }
          100% {
            transform: rotate(270deg);
          }
        }

        @keyframes fadeIn {
          0% {
            opacity: 0;
            transform: translateY(-10px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
