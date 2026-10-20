
import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  HeartPulse,
  Moon,
  Footprints,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  UserRound,
  BrainCircuit,
  Clock3,
  LayoutDashboard,
  TrendingUp
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts'

const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function Stat({ icon: Icon, label, value, unit, note }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className="stat-icon"><Icon size={17} /></span>
      </div>
      <div className="stat-value">
        {value}<small>{unit}</small>
      </div>
      <div className="stat-note">{note}</div>
    </div>
  )
}

function App() {
  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('P-1001')
  const [patient, setPatient] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [carbs, setCarbs] = useState(55)
  const [stress, setStress] = useState(4)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [apiOk, setApiOk] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  async function loadPatient(id = patientId) {
    setError('')

    try {
      const [pRes, tRes] = await Promise.all([
        fetch(`${API}/api/patients/${id}`),
        fetch(`${API}/api/patients/${id}/timeline`)
      ])

      if (!pRes.ok || !tRes.ok) {
        throw new Error('Could not load patient. Check the backend and generated data.')
      }

      const patientData = await pRes.json()
      const timelineData = await tRes.json()

      setPatient(patientData)
      setTimeline(Array.isArray(timelineData) ? timelineData : [])
      setApiOk(true)
    } catch (e) {
      setError(e.message || 'Unable to load patient.')
      setApiOk(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function initialize() {
      try {
        const res = await fetch(`${API}/api/patients`)

        if (!res.ok) throw new Error('API unavailable')

        const data = await res.json()

        if (cancelled) return

        setPatients(data)

        if (data.length > 0) {
          const initialId = data.some(p => p.patient_id === 'P-1001')
            ? 'P-1001'
            : data[0].patient_id

          setPatientId(initialId)
          await loadPatient(initialId)
        } else {
          setError('No synthetic patients found. Generate the dataset first.')
        }
      } catch {
        if (!cancelled) {
          setError('Backend is not connected. Start FastAPI and try again.')
          setApiOk(false)
        }
      }
    }

    initialize()

    return () => {
      cancelled = true
    }
  }, [])

  async function runPrediction() {
    if (!patient) return

    setLoading(true)
    setError('')
    setPrediction(null)

    try {
      const res = await fetch(`${API}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          patient_id: patientId,
          meal_carbs_g: Number(carbs),
          stress_level: Number(stress)
        })
      })

      const body = await res.json()

      if (!res.ok) {
        throw new Error(body.detail || 'Prediction failed')
      }

      setPrediction(body)
    } catch (e) {
      setError(e.message || 'Unable to run prediction.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    return timeline.map((r, i) => ({
      ...r,
      label: new Date(r.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      }),
      index: i
    }))
  }, [timeline])

  const riskPct = prediction
    ? Math.round(prediction.risk_probability * 100)
    : null

  const pageInfo = {
    overview: {
      title: 'Patient overview',
      subtitle: 'Explore a synthetic patient profile and glucose-spike risk.'
    },
    signals: {
      title: 'Metabolic signals',
      subtitle: 'Explore wearable time-series data and historical health indicators.'
    },
    risk: {
      title: 'Risk intelligence',
      subtitle: 'Run an experimental two-hour glucose-spike risk simulation.'
    }
  }

  function NavigationItem({ id, icon: Icon, children }) {
    return (
      <button
        type="button"
        className={`nav-item ${activeTab === id ? 'active' : ''}`}
        aria-current={activeTab === id ? 'page' : undefined}
        onClick={() => {
          setActiveTab(id)
          setError('')
        }}
      >
        <Icon size={17} />
        <span>{children}</span>
      </button>
    )
  }

  function PatientSelector() {
    return (
      <div className="patient-card">
        <div className="avatar">
          <UserRound size={27} />
        </div>

        <div className="patient-meta">
          <span className="eyebrow">SELECTED SYNTHETIC PATIENT</span>
          <h2>{patient?.patient_id || patientId}</h2>
          <p>
            {patient
              ? `${patient.age} years · ${patient.sex} · ${patient.diabetes_duration_years} years since diagnosis`
              : 'Loading patient profile...'}
          </p>
        </div>

        <select
          aria-label="Select synthetic patient"
          value={patientId}
          onChange={e => {
            const id = e.target.value
            setPatientId(id)
            setPatient(null)
            setPrediction(null)
            loadPatient(id)
          }}
        >
          {patients.map(p => (
            <option key={p.patient_id} value={p.patient_id}>
              {p.patient_id} · HbA1c {p.hba1c_percent}%
            </option>
          ))}
        </select>
      </div>
    )
  }

  function Disclaimer() {
    return (
      <div className="disclaimer">
        <ShieldCheck size={19} />
        <div>
          <b>Prototype, not clinical advice</b>
          <p>All data and predictions are synthetic. Not validated for medical decisions.</p>
        </div>
      </div>
    )
  }

  function GlucoseChart({ height = '280px' }) {
    return (
      <div className="chart" style={{ height }}>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="glucoseFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7c5cff" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#7c5cff" stopOpacity={0.01} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#edf0f5" />

              <XAxis
                dataKey="label"
                tick={{ fontSize: 10, fill: '#8a93a5' }}
                interval="preserveStartEnd"
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                domain={['dataMin - 10', 'dataMax + 10']}
                tick={{ fontSize: 10, fill: '#8a93a5' }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip />

              <Area
                type="monotone"
                dataKey="glucose_mg_dl"
                name="Glucose mg/dL"
                stroke="#7c5cff"
                strokeWidth={2.5}
                fill="url(#glucoseFill)"
                dot={false}
                connectNulls
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-state">
            No timeline data available for this patient.
          </div>
        )}
      </div>
    )
  }

  function EHRPanel() {
    return (
      <div className="panel ehr-panel">
        <div className="panel-heading">
          <div>
            <h3>Historical EHR snapshot</h3>
            <p>Static patient features</p>
          </div>
          <span className="pill">EHR</span>
        </div>

        <div className="ehr-list">
          <div>
            <span>HbA1c</span>
            <b>{patient?.hba1c_percent ?? '—'}<small>%</small></b>
          </div>

          <div>
            <span>Medication adherence proxy</span>
            <b>
              {patient
                ? `${Math.round(patient.medication_adherence_proxy * 100)}%`
                : '—'}
            </b>
          </div>

          <div>
            <span>Hypertension history</span>
            <b>
              {patient
                ? patient.hypertension
                  ? 'Present'
                  : 'Not recorded'
                : '—'}
            </b>
          </div>

          <div>
            <span>Patient type</span>
            <b>Simulated T2D</b>
          </div>
        </div>
      </div>
    )
  }

  function SignalFusionPanel() {
    return (
      <div className="panel signal-panel">
        <div className="panel-heading">
          <div>
            <h3>Signal fusion</h3>
            <p>Historical and dynamic inputs</p>
          </div>
        </div>

        <div className="signal-row">
          <span className="signal-icon purple-bg">
            <Activity size={16} />
          </span>
          <div>
            <b>Wearable time series</b>
            <small>Glucose trend, heart rate, HRV, sleep and steps</small>
          </div>
          <span className="signal-status">SIMULATED</span>
        </div>

        <div className="signal-row">
          <span className="signal-icon blue-bg">
            <UserRound size={16} />
          </span>
          <div>
            <b>Historical EHR</b>
            <small>Age, HbA1c, diabetes duration and adherence proxy</small>
          </div>
          <span className="signal-status">STATIC</span>
        </div>

        <div className="signal-row">
          <span className="signal-icon amber-bg">
            <Clock3 size={16} />
          </span>
          <div>
            <b>Scenario context</b>
            <small>Carbohydrate intake and stress estimate</small>
          </div>
          <span className="signal-status">INPUT</span>
        </div>

        <div className="model-note">
          <AlertTriangle size={15} />
          <span>
            Risk categories are illustrative thresholds over synthetic labels,
            not medical cut-offs.
          </span>
        </div>
      </div>
    )
  }

  function PredictionPanel() {
    return (
      <div className="panel prediction-panel">
        <div className="panel-heading">
          <div>
            <h3>Two-hour risk simulation</h3>
            <p>Adjust the scenario inputs and run the model.</p>
          </div>
          <div className="model-chip">
            <BrainCircuit size={15} /> Random Forest
          </div>
        </div>

        <div className="controls-grid">
          <label>
            Meal carbohydrate estimate <b>{carbs} g</b>
            <input
              type="range"
              min="0"
              max="150"
              step="5"
              value={carbs}
              onChange={e => setCarbs(Number(e.target.value))}
            />
            <small>Scenario input only</small>
          </label>

          <label>
            Stress level <b>{stress}/10</b>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={stress}
              onChange={e => setStress(Number(e.target.value))}
            />
            <small>Self-reported simulation input</small>
          </label>
        </div>

        <button
          type="button"
          className="primary-btn"
          onClick={runPrediction}
          disabled={loading || !patient}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          {loading ? 'Running model…' : 'Run risk prediction'}
        </button>

        {prediction && (
          <div className="risk-result">
            <div className="risk-score">
              <span>Illustrative risk score</span>
              <strong>{riskPct}%</strong>
              <div className="risk-track">
                <i style={{ width: `${Math.max(0, Math.min(100, riskPct))}%` }} />
              </div>
            </div>

            <div className="risk-detail">
              <span className={`risk-tag ${String(prediction.risk_category).toLowerCase()}`}>
                {prediction.risk_category} simulated risk
              </span>
              <p>
                {prediction.prediction_label} over {prediction.horizon_hours} hours.
              </p>
              <small>{prediction.disclaimer}</small>
            </div>
          </div>
        )}

        <div className="model-note">
          <AlertTriangle size={15} />
          <span>
            Experimental prediction based on synthetic data. This score is
            not a clinically validated probability and must not guide treatment.
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Activity size={23} />
          </div>
          <div>
            <strong>GlucoTwin</strong>
            <small>Digital Patient Twin</small>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          <NavigationItem id="overview" icon={LayoutDashboard}>
            Patient overview
          </NavigationItem>

          <NavigationItem id="signals" icon={HeartPulse}>
            Metabolic signals
          </NavigationItem>

          <NavigationItem id="risk" icon={BrainCircuit}>
            Risk intelligence
          </NavigationItem>
        </nav>

        <div className="sidebar-bottom">
          <ShieldCheck size={18} />
          <div>
            <b>Privacy-first demo</b>
            <small>Synthetic data only</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">DIGITAL TWIN CHALLENGE 2026</div>
            <h1>{pageInfo[activeTab].title}</h1>
            <p>{pageInfo[activeTab].subtitle}</p>
          </div>

          <div className={`connection ${apiOk ? 'online' : ''}`}>
            <span />
            {apiOk ? 'API connected' : 'Waiting for API'}
          </div>
        </header>

        {error && (
          <div className="error-banner" role="alert">
            <AlertTriangle size={17} />
            {error}
          </div>
        )}

        <section className="patient-row">
          <PatientSelector />
          <Disclaimer />
        </section>

        {activeTab === 'overview' && (
          <>
            <section className="stats-grid">
              <Stat
                icon={Activity}
                label="Latest glucose"
                value={patient?.latest_glucose_mg_dl ?? '—'}
                unit="mg/dL"
                note="Latest simulated sensor reading"
              />

              <Stat
                icon={HeartPulse}
                label="Heart rate"
                value={patient?.latest_heart_rate_bpm ?? '—'}
                unit="bpm"
                note="Wearable-style signal"
              />

              <Stat
                icon={Moon}
                label="Sleep"
                value={patient?.latest_sleep_hours ?? '—'}
                unit="hrs"
                note="Synthetic recent sleep estimate"
              />

              <Stat
                icon={Footprints}
                label="Steps / hour"
                value={patient?.latest_steps ?? '—'}
                unit=""
                note="Recent activity window"
              />
            </section>

            <section className="content-grid">
              <div className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Glucose timeline</h3>
                    <p>Recent sensor readings · synthetic time series</p>
                  </div>
                  <span className="pill">
                    <span className="dot purple" /> Glucose
                  </span>
                </div>
                <GlucoseChart />
              </div>

              <EHRPanel />
            </section>

            <section className="prediction-section">
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Quick risk assessment</h3>
                    <p>Explore a two-hour glucose-spike scenario.</p>
                  </div>
                </div>

                <p>
                  Adjust inputs and run an experimental prediction using the
                  selected synthetic patient's profile.
                </p>

                <button
                  type="button"
                  className="primary-btn"
                  onClick={() => setActiveTab('risk')}
                >
                  <BrainCircuit size={16} />
                  Open Risk intelligence
                </button>
              </div>

              <SignalFusionPanel />
            </section>
          </>
        )}

        {activeTab === 'signals' && (
          <>
            <section className="stats-grid">
              <Stat
                icon={Activity}
                label="Latest glucose"
                value={patient?.latest_glucose_mg_dl ?? '—'}
                unit="mg/dL"
                note="Latest simulated sensor reading"
              />

              <Stat
                icon={HeartPulse}
                label="Heart rate"
                value={patient?.latest_heart_rate_bpm ?? '—'}
                unit="bpm"
                note="Wearable heart-rate signal"
              />

              <Stat
                icon={Moon}
                label="Sleep"
                value={patient?.latest_sleep_hours ?? '—'}
                unit="hrs"
                note="Recent synthetic sleep estimate"
              />

              <Stat
                icon={Footprints}
                label="Steps / hour"
                value={patient?.latest_steps ?? '—'}
                unit=""
                note="Recent activity window"
              />
            </section>

            <section className="content-grid">
              <div className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Wearable glucose timeline</h3>
                    <p>Timestamped sensor readings for the selected patient</p>
                  </div>
                  <span className="pill">TIME SERIES</span>
                </div>
                <GlucoseChart height="340px" />
              </div>

              <EHRPanel />
            </section>

            <section className="prediction-section">
              <SignalFusionPanel />
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Signal interpretation</h3>
                    <p>Context for the selected synthetic patient</p>
                  </div>
                  <TrendingUp size={19} />
                </div>

                <div className="ehr-list">
                  <div>
                    <span>Recorded sensor samples</span>
                    <b>{timeline.length}</b>
                  </div>
                  <div>
                    <span>Selected patient</span>
                    <b>{patient?.patient_id ?? '—'}</b>
                  </div>
                  <div>
                    <span>Historical HbA1c</span>
                    <b>{patient?.hba1c_percent ?? '—'}%</b>
                  </div>
                </div>

                <p>
                  Sensor observations are synthetic. They demonstrate how
                  dynamic measurements can be viewed alongside historical EHR
                  features; they do not establish a clinical diagnosis.
                </p>
              </div>
            </section>
          </>
        )}

        {activeTab === 'risk' && (
          <>
            <section className="stats-grid">
              <Stat
                icon={Activity}
                label="Current glucose"
                value={patient?.latest_glucose_mg_dl ?? '—'}
                unit="mg/dL"
                note="Latest synthetic reading"
              />

              <Stat
                icon={HeartPulse}
                label="Heart rate"
                value={patient?.latest_heart_rate_bpm ?? '—'}
                unit="bpm"
                note="Latest wearable-style signal"
              />

              <Stat
                icon={TrendingUp}
                label="HbA1c"
                value={patient?.hba1c_percent ?? '—'}
                unit="%"
                note="Historical EHR measurement"
              />

              <Stat
                icon={Clock3}
                label="Prediction horizon"
                value="2"
                unit="hrs"
                note="Intended forecast window"
              />
            </section>

            <section className="prediction-section">
              <PredictionPanel />
              <SignalFusionPanel />
            </section>

            <section className="content-grid">
              <div className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Recent glucose context</h3>
                    <p>Wearable-style time series for this patient</p>
                  </div>
                </div>
                <GlucoseChart />
              </div>

              <EHRPanel />
            </section>
          </>
        )}

        <footer>
          GlucoTwin · Happiest Health Digital Twin Challenge 2026 ·
          Synthetic proof of concept
        </footer>
      </main>
    </div>
  )
}

export default App
