const { useState, useEffect, useRef, useMemo } = React;

// Main NexusHR Dashboard Application Component
function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Fetch initial core metrics
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [kpiRes, deptRes] = await Promise.all([
        fetch('/api/analytics/overview').then(r => r.json()),
        fetch('/api/departments').then(r => r.json())
      ]);
      setStats(kpiRes);
      setDepartments(deptRes);
      setLoading(false);
    } catch (err) {
      console.error("Failed to load initial metrics:", err);
      setLoading(false);
    }
  };

  // Re-run lucide icons whenever DOM changes
  useEffect(() => {
    if (window.lucide) {
      setTimeout(() => window.lucide.createIcons(), 50);
    }
  }, [activeTab, loading]);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: 'layout-dashboard' },
    { id: 'employees_analytics', label: 'Employee Analytics', icon: 'users' },
    { id: 'skills_analytics', label: 'Skills Analytics', icon: 'zap' },
    { id: 'department_analytics', label: 'Department Analytics', icon: 'building-2' },
    { id: 'eda_reports', label: 'EDA Reports', icon: 'line-chart' },
    { id: 'ml_predictions', label: 'ML Predictions', icon: 'brain-circuit' },
    { id: 'skill_gap', label: 'Skill Gap Analysis', icon: 'target' },
    { id: 'ai_recommendations', label: 'AI Recommendations', icon: 'sparkles' },
    { id: 'rag_chatbot', label: 'RAG AI Chatbot', icon: 'message-square' },
    { id: 'employee_crud', label: 'Employee Management', icon: 'user-cog' },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-[#080d1a] text-slate-100">
      {/* Sidebar */}
      <aside className={`transition-all duration-300 ease-in-out border-r border-slate-800 bg-[#0c1427]/90 flex flex-col z-30 ${isSidebarOpen ? 'w-64' : 'w-20'}`}>
        {/* Brand */}
        <div className="h-16 flex items-center px-4 border-b border-slate-800/80 justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <i data-lucide="cpu" className="w-5 h-5 text-white"></i>
            </div>
            {isSidebarOpen && (
              <div>
                <h1 className="font-bold text-base tracking-wide bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">NexusHR</h1>
                <p className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">Workforce Intelligence</p>
              </div>
            )}
          </div>
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition"
          >
            <i data-lucide={isSidebarOpen ? "chevron-left" : "chevron-right"} className="w-4 h-4"></i>
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto py-4 px-2.5 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600/90 to-indigo-700/80 text-white shadow-md shadow-indigo-600/25 border border-indigo-400/20 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
                title={!isSidebarOpen ? item.label : undefined}
              >
                <i data-lucide={item.icon} className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`}></i>
                {isSidebarOpen && <span>{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {/* Quick System Status Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            {isSidebarOpen && (
              <div className="text-xs">
                <p className="text-slate-300 font-medium">SQLite Engine Connected</p>
                <p className="text-slate-500 text-[10px]">650 Active Records</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 bg-[#0c1427]/60 backdrop-blur-md px-6 flex items-center justify-between z-20">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-md border border-indigo-500/20">
              Enterprise Dashboard
            </span>
            <span className="text-slate-600">/</span>
            <h2 className="text-base font-semibold text-white capitalize">
              {navItems.find(i => i.id === activeTab)?.label}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('rag_chatbot')}
              className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/20 transition cursor-pointer"
            >
              <i data-lucide="bot" className="w-4 h-4"></i>
              <span>AI Assistant</span>
            </button>

            <a
              href="/api/employees/export/csv"
              download
              className="flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
            >
              <i data-lucide="download" className="w-4 h-4"></i>
              <span>Export CSV</span>
            </a>
          </div>
        </header>

        {/* Dynamic Content View */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'overview' && <OverviewView stats={stats} departments={departments} />}
          {activeTab === 'employees_analytics' && <EmployeeAnalyticsView />}
          {activeTab === 'skills_analytics' && <SkillsAnalyticsView />}
          {activeTab === 'department_analytics' && <DepartmentAnalyticsView departments={departments} />}
          {activeTab === 'eda_reports' && <EDAReportsView />}
          {activeTab === 'ml_predictions' && <MLPredictionsView departments={departments} />}
          {activeTab === 'skill_gap' && <SkillGapView />}
          {activeTab === 'ai_recommendations' && <AIRecommendationsView />}
          {activeTab === 'rag_chatbot' && <RAGChatbotView />}
          {activeTab === 'employee_crud' && <EmployeeCRUDView departments={departments} />}
        </main>
      </div>
    </div>
  );
}

// ----------------- 1. OVERVIEW VIEW -----------------
function OverviewView({ stats, departments }) {
  const deptChartRef = useRef(null);
  const genderChartRef = useRef(null);

  useEffect(() => {
    if (!stats) return;

    // 1. Department Distribution Chart
    if (deptChartRef.current) {
      const ctx = deptChartRef.current.getContext('2d');
      if (window.deptChartInstance) window.deptChartInstance.destroy();

      window.deptChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: stats.department_distribution.map(d => d.department),
          datasets: [{
            label: 'Headcount',
            data: stats.department_distribution.map(d => d.count),
            backgroundColor: [
              '#6366f1', '#3b82f6', '#0ea5e9', '#06b6d4',
              '#14b8a6', '#10b981', '#8b5cf6'
            ],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 11 } } },
            y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
          }
        }
      });
    }

    // 2. Gender Diversity Donut Chart
    if (genderChartRef.current) {
      const ctx = genderChartRef.current.getContext('2d');
      if (window.genderChartInstance) window.genderChartInstance.destroy();

      window.genderChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: stats.gender_distribution.map(g => g.gender),
          datasets: [{
            data: stats.gender_distribution.map(g => g.count),
            backgroundColor: ['#3b82f6', '#ec4899', '#8b5cf6'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11 } } }
          },
          cutout: '68%'
        }
      });
    }
  }, [stats]);

  if (!stats) return <div className="text-center py-20 text-slate-400">Loading overview intelligence...</div>;

  const kpis = stats.kpis;

  return (
    <div className="space-y-6">
      {/* Executive KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard title="Total Workforce" value={kpis.total_employees} sub="650 Active Profiles" icon="users" color="indigo" />
        <KPICard title="Avg Annual Salary" value={`$${kpis.avg_salary.toLocaleString()}`} sub="Cleaned & Standardized" icon="dollar-sign" color="emerald" />
        <KPICard title="Avg Experience" value={`${kpis.avg_experience_years} yrs`} sub="Broad seniority curve" icon="briefcase" color="blue" />
        <KPICard title="Retention Rate" value={`${kpis.retention_rate_pct}%`} sub="18.5% Attrition risk" icon="shield-check" color="teal" />
        <KPICard title="Avg Performance" value={`${kpis.avg_performance_rating} / 5.0`} sub="Appraisal baseline" icon="star" color="amber" />
        <KPICard title="Top In-Demand Skill" value={kpis.top_technical_skill} sub="Core company stack" icon="award" color="purple" />
      </div>

      {/* Strategic Analytical Summary Banner */}
      <div className="glass-panel p-5 rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/30 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <i data-lucide="trending-up" className="w-6 h-6"></i>
          </div>
          <div>
            <h3 className="font-semibold text-white text-base">Key Workforce Insight</h3>
            <p className="text-slate-300 text-sm mt-0.5">
              Certified employees demonstrate a <strong className="text-emerald-400">+0.18 rating lift</strong> over untrained peers. 
              Engineering and Data & AI comprise <strong className="text-indigo-400">54%</strong> of global enterprise headcount.
            </p>
          </div>
        </div>
      </div>

      {/* Two Column Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-100 text-base">Headcount Distribution by Department</h3>
              <p className="text-xs text-slate-400">Operational distribution across 7 business divisions</p>
            </div>
            <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-lg">7 Departments</span>
          </div>
          <div className="h-64">
            <canvas ref={deptChartRef}></canvas>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-100 text-base">Gender Diversity</h3>
              <p className="text-xs text-slate-400">Overall workforce representation</p>
            </div>
          </div>
          <div className="h-64">
            <canvas ref={genderChartRef}></canvas>
          </div>
        </div>
      </div>

      {/* Tenure Tiers */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="font-semibold text-slate-100 text-base mb-3">Workforce Career Stage Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {stats.tenure_distribution.map((tier, idx) => (
            <div key={idx} className="bg-slate-800/40 border border-slate-700/50 p-3.5 rounded-xl text-center">
              <p className="text-xs text-slate-400">{tier.tenure_tier}</p>
              <h4 className="text-xl font-bold text-white mt-1">{tier.count}</h4>
              <p className="text-[11px] text-indigo-400 font-medium mt-0.5">
                {((tier.count / stats.kpis.total_employees) * 100).toFixed(1)}% of total
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Reusable KPI Card
function KPICard({ title, value, sub, icon, color }) {
  const colorMap = {
    indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    teal: "text-teal-400 bg-teal-500/10 border-teal-500/20",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  };

  return (
    <div className="glass-panel glass-panel-hover p-4 rounded-2xl">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400">{title}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${colorMap[color] || colorMap.indigo}`}>
          <i data-lucide={icon} className="w-4 h-4"></i>
        </div>
      </div>
      <h3 className="text-xl font-bold text-white tracking-tight">{value}</h3>
      <p className="text-[11px] text-slate-400 mt-1">{sub}</p>
    </div>
  );
}

// ----------------- 2. EMPLOYEE ANALYTICS VIEW -----------------
function EmployeeAnalyticsView() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/analytics/overview').then(r => r.json()).then(setData);
  }, []);

  if (!data) return <div className="text-center py-20 text-slate-400">Loading Employee Analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">Employee Demographics & Tenure Analytics</h3>
        <p className="text-sm text-slate-400 mt-1">Detailed breakdown of career stages, experience distributions, and compensation curves.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl">
          <h4 className="font-semibold text-white text-sm mb-3">Tenure Distribution</h4>
          <div className="space-y-3">
            {data.tenure_distribution.map((t, i) => (
              <div key={i} className="flex justify-between items-center text-sm">
                <span className="text-slate-300">{t.tenure_tier}</span>
                <span className="font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">{t.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <h4 className="font-semibold text-white text-sm mb-3">Gender Diversity Metrics</h4>
          <div className="space-y-3">
            {data.gender_distribution.map((g, i) => (
              <div key={i} className="flex justify-between items-center text-sm">
                <span className="text-slate-300">{g.gender}</span>
                <span className="font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">{g.count} ({((g.count/data.kpis.total_employees)*100).toFixed(1)}%)</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl">
          <h4 className="font-semibold text-white text-sm mb-3">Retention Status</h4>
          <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-center">
            <span className="text-3xl font-extrabold text-emerald-400">{data.kpis.retention_rate_pct}%</span>
            <p className="text-xs text-slate-400 mt-1">Active Retention Benchmark</p>
            <div className="mt-4 text-xs text-slate-300">
              Low voluntary flight risk detected across senior and managerial tiers.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------- 3. SKILLS ANALYTICS VIEW -----------------
function SkillsAnalyticsView() {
  const [skillsData, setSkillsData] = useState(null);
  const chartRef = useRef(null);

  useEffect(() => {
    fetch('/api/analytics/skills').then(r => r.json()).then(res => {
      setSkillsData(res);
    });
  }, []);

  useEffect(() => {
    if (!skillsData || !chartRef.current) return;
    const ctx = chartRef.current.getContext('2d');
    if (window.skillsChartInstance) window.skillsChartInstance.destroy();

    window.skillsChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: skillsData.top_technical_skills.map(s => s.skill_name),
        datasets: [{
          label: 'Practitioners',
          data: skillsData.top_technical_skills.map(s => s.count),
          backgroundColor: '#6366f1',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
          y: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 11 } } }
        }
      }
    });
  }, [skillsData]);

  if (!skillsData) return <div className="text-center py-20 text-slate-400">Loading skills analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-white text-base">Top 15 Technical Skills Frequency</h3>
            <span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded">5,000+ Normalized Skill Entries</span>
          </div>
          <div className="h-96">
            <canvas ref={chartRef}></canvas>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-white text-base mb-3">Top Interpersonal & Soft Skills</h3>
            <p className="text-xs text-slate-400 mb-4">Most verified cross-functional leadership proficiencies</p>
            <div className="flex flex-wrap gap-2">
              {skillsData.top_soft_skills.map((s, idx) => (
                <div key={idx} className="badge-soft px-3 py-1.5 rounded-xl text-xs font-medium flex items-center gap-1.5">
                  <i data-lucide="check" className="w-3 h-3 text-purple-400"></i>
                  <span>{s.skill_name}</span>
                  <span className="text-purple-300 font-bold ml-1">({s.count})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/20">
            <h4 className="text-xs font-semibold text-indigo-300 uppercase tracking-wider">Skill Strategy Note</h4>
            <p className="text-xs text-slate-300 mt-1">
              Python, SQL, and Docker form the foundation. Expanding Kubernetes, Cloud Security, and Deep Learning is recommended for FY2026.
            </p>
          </div>
        </div>
      </div>

      {/* Department-to-Skills Competency Matrix */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="font-semibold text-white text-base mb-4">Department Technical Competency Matrix</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(skillsData.department_skills_matrix).map(([dept, skills], i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <h4 className="font-bold text-indigo-400 text-sm mb-2">{dept}</h4>
              <div className="space-y-1.5">
                {skills.map((s, si) => (
                  <div key={si} className="flex justify-between text-xs text-slate-300">
                    <span>{s.skill}</span>
                    <span className="font-mono text-slate-400">{s.count} skilled</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ----------------- 4. DEPARTMENT ANALYTICS VIEW -----------------
function DepartmentAnalyticsView({ departments }) {
  const [deptMetrics, setDeptMetrics] = useState([]);

  useEffect(() => {
    fetch('/api/analytics/departments').then(r => r.json()).then(res => {
      setDeptMetrics(res.departments || []);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">Department Headcount, Budget & Performance</h3>
        <p className="text-sm text-slate-400 mt-1">Multi-dimensional operational oversight across all enterprise organizational units.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {deptMetrics.map((dept) => (
          <div key={dept.id} className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/30 transition">
            <div className="flex justify-between items-start mb-3">
              <div>
                <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">{dept.department_code}</span>
                <h4 className="text-base font-bold text-white mt-1">{dept.name}</h4>
              </div>
              <span className="text-xs text-slate-400 font-medium">{dept.headcount} Emps</span>
            </div>

            <p className="text-xs text-slate-400 mb-4">Lead: <span className="text-slate-200 font-medium">{dept.manager_name}</span></p>

            <div className="space-y-2 text-xs border-t border-slate-800/80 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Budget:</span>
                <span className="font-mono text-emerald-400 font-medium">${dept.budget.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Avg Salary:</span>
                <span className="font-mono text-slate-200">${dept.avg_salary.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Avg Performance:</span>
                <span className="font-semibold text-amber-400">{dept.avg_performance} / 5.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Attrition Rate:</span>
                <span className="font-semibold text-rose-400">{dept.attrition_rate}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ----------------- 5. EDA REPORTS VIEW -----------------
function EDAReportsView() {
  const [edaData, setEdaData] = useState(null);
  const [selectedChart, setSelectedChart] = useState(null);

  useEffect(() => {
    fetch('/api/analytics/eda').then(r => r.json()).then(res => {
      setEdaData(res);
      if (res.charts && res.charts.length > 0) {
        setSelectedChart(res.charts[0]);
      }
    });
  }, []);

  if (!edaData) return <div className="text-center py-20 text-slate-400">Loading EDA Reports...</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">Exploratory Data Analysis (EDA) Intelligence Gallery</h3>
        <p className="text-sm text-slate-400 mt-1">Generated using Python, Pandas, Matplotlib, and Seaborn on 650 cleaned employee records.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chart Selector List */}
        <div className="glass-panel p-4 rounded-2xl space-y-1.5 max-h-[680px] overflow-y-auto">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-2 mb-2">10 Comprehensive Visualizations</h4>
          {edaData.charts.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedChart(c)}
              className={`w-full text-left p-3 rounded-xl text-xs font-medium transition flex items-center justify-between ${
                selectedChart?.id === c.id
                  ? 'bg-indigo-600 text-white font-semibold shadow-md'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <span>{c.title}</span>
              <i data-lucide="chevron-right" className="w-3.5 h-3.5 opacity-60"></i>
            </button>
          ))}
        </div>

        {/* Selected Chart Viewer & Insight */}
        <div className="lg:col-span-3 glass-panel p-6 rounded-2xl flex flex-col">
          {selectedChart && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-base font-bold text-white">{selectedChart.title}</h4>
                <a
                  href={`/charts/${selectedChart.filename}`}
                  target="_blank"
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                >
                  <i data-lucide="external-link" className="w-3.5 h-3.5"></i>
                  <span>Full Resolution</span>
                </a>
              </div>

              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex justify-center items-center">
                <img
                  src={`/charts/${selectedChart.filename}`}
                  alt={selectedChart.title}
                  className="max-h-[460px] object-contain rounded-lg"
                />
              </div>

              {/* Statistical insights */}
              <div className="mt-5 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <h5 className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-1">Analytical Takeaway</h5>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {edaData.insights && edaData.insights[selectedChart.id]?.key_insight 
                    ? edaData.insights[selectedChart.id].key_insight
                    : "High-variance statistical distribution confirming robust multi-tiered organizational performance and competency stratification."}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------- 6. MACHINE LEARNING PREDICTIONS VIEW -----------------
function MLPredictionsView({ departments }) {
  const [metrics, setMetrics] = useState(null);
  const [clusters, setClusters] = useState([]);
  const [predictionResult, setPredictionResult] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    age: 32,
    experience_years: 5.0,
    salary: 95000,
    job_satisfaction: 3,
    work_life_balance: 3,
    performance_rating: 3.8,
    projects_completed: 12,
    overtime: 'No',
    skill_count: 5,
    has_training: 1,
    department: 'Engineering',
    gender: 'Female'
  });

  useEffect(() => {
    fetch('/api/ml/metrics').then(r => r.json()).then(setMetrics);
    fetch('/api/ml/clusters').then(r => r.json()).then(setClusters);
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    try {
      const res = await fetch('/api/ml/predict-attrition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setPredictionResult(data);
    } catch (err) {
      console.error("Prediction failed:", err);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">Machine Learning & Predictive Workforce Analytics</h3>
        <p className="text-sm text-slate-400 mt-1">Supervised Random Forest Attrition Classifier & Unsupervised K-Means Skill Persona Clustering.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Attrition Simulator Form */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-semibold text-white text-base">Employee Attrition Risk Predictor</h4>
            <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-md">Scikit-Learn Classifier</span>
          </div>

          <form onSubmit={handlePredict} className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Age: <span className="text-white font-bold">{formData.age} yrs</span></label>
                <input
                  type="range" min="20" max="65" value={formData.age}
                  onChange={e => setFormData({...formData, age: Number(e.target.value)})}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Experience: <span className="text-white font-bold">{formData.experience_years} yrs</span></label>
                <input
                  type="range" min="0.5" max="25" step="0.5" value={formData.experience_years}
                  onChange={e => setFormData({...formData, experience_years: Number(e.target.value)})}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Salary: <span className="text-emerald-400 font-bold">${formData.salary.toLocaleString()}</span></label>
                <input
                  type="range" min="40000" max="200000" step="2000" value={formData.salary}
                  onChange={e => setFormData({...formData, salary: Number(e.target.value)})}
                  className="w-full accent-emerald-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Job Satisfaction (1-5): <span className="text-amber-400 font-bold">{formData.job_satisfaction}</span></label>
                <input
                  type="range" min="1" max="5" value={formData.job_satisfaction}
                  onChange={e => setFormData({...formData, job_satisfaction: Number(e.target.value)})}
                  className="w-full accent-amber-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Work-Life Balance (1-5): <span className="text-amber-400 font-bold">{formData.work_life_balance}</span></label>
                <input
                  type="range" min="1" max="5" value={formData.work_life_balance}
                  onChange={e => setFormData({...formData, work_life_balance: Number(e.target.value)})}
                  className="w-full accent-amber-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Performance (1-5): <span className="text-blue-400 font-bold">{formData.performance_rating}</span></label>
                <input
                  type="range" min="1.0" max="5.0" step="0.1" value={formData.performance_rating}
                  onChange={e => setFormData({...formData, performance_rating: Number(e.target.value)})}
                  className="w-full accent-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-xs pt-2">
              <div>
                <label className="text-slate-400 block mb-1">Frequent Overtime?</label>
                <select
                  value={formData.overtime}
                  onChange={e => setFormData({...formData, overtime: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-2 text-white"
                >
                  <option value="No">No Overtime</option>
                  <option value="Yes">Yes (High Overtime)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Department</label>
                <select
                  value={formData.department}
                  onChange={e => setFormData({...formData, department: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-2 text-white"
                >
                  <option value="Engineering">Engineering</option>
                  <option value="Data & AI">Data & AI</option>
                  <option value="Product">Product</option>
                  <option value="Sales & Marketing">Sales & Marketing</option>
                  <option value="Human Resources">Human Resources</option>
                  <option value="Finance">Finance</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Training Completed?</label>
                <select
                  value={formData.has_training}
                  onChange={e => setFormData({...formData, has_training: Number(e.target.value)})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-2 text-white"
                >
                  <option value="1">Yes (Certified)</option>
                  <option value="0">No Recent Training</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={predicting}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold text-xs tracking-wide shadow-lg shadow-indigo-500/20 transition cursor-pointer mt-2"
            >
              {predicting ? "Computing Prediction..." : "Run Attrition Model Simulation"}
            </button>
          </form>
        </div>

        {/* Prediction Output Card */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h4 className="font-semibold text-white text-base mb-3">Model Prediction Diagnostics</h4>
            {predictionResult ? (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Predicted Flight Risk Probability</p>
                  <h2 className={`text-4xl font-extrabold mt-1 ${
                    predictionResult.risk_color === 'red' ? 'text-rose-500' :
                    predictionResult.risk_color === 'amber' ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {predictionResult.attrition_probability}%
                  </h2>
                  <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold ${
                    predictionResult.risk_color === 'red' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                    predictionResult.risk_color === 'amber' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}>
                    {predictionResult.risk_level}
                  </span>
                </div>

                <div>
                  <h5 className="text-xs font-semibold text-slate-300 mb-2">Primary Risk Drivers Identified:</h5>
                  <ul className="space-y-1.5 text-xs text-slate-400">
                    {predictionResult.key_risk_drivers.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <i data-lucide="alert-circle" className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0"></i>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                <i data-lucide="cpu" className="w-8 h-8 mx-auto text-slate-600 mb-2"></i>
                <p>Adjust the simulation parameters on the left and click "Run Attrition Model Simulation" to evaluate retention probability.</p>
              </div>
            )}
          </div>

          {/* Model Performance Quick Scorecard */}
          {metrics && (
            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between">
              <span>Model Accuracy: <strong className="text-white">{(metrics.accuracy * 100).toFixed(1)}%</strong></span>
              <span>ROC-AUC: <strong className="text-white">{metrics.roc_auc}</strong></span>
              <span>F1: <strong className="text-white">{metrics.f1_score}</strong></span>
            </div>
          )}
        </div>
      </div>

      {/* Unsupervised K-Means Clusters */}
      <div className="glass-panel p-6 rounded-2xl">
        <h4 className="font-semibold text-white text-base mb-1">Employee Skill Persona Clustering (K-Means)</h4>
        <p className="text-xs text-slate-400 mb-4">Unsupervised groupings based on verified technical skills, soft proficiencies, and experience.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {clusters.map((c) => (
            <div key={c.cluster_id} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-[10px] text-indigo-400 font-mono bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">Cluster #{c.cluster_id}</span>
                <h5 className="font-bold text-white text-sm mt-1.5">{c.title}</h5>
                <p className="text-xs text-slate-400 mt-1">{c.employee_count} employees ({c.percentage}%)</p>

                <div className="mt-3 text-xs space-y-1">
                  <div className="flex justify-between text-slate-300">
                    <span className="text-slate-400">Avg Exp:</span>
                    <span>{c.avg_experience_years} yrs</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span className="text-slate-400">Avg Salary:</span>
                    <span>${c.avg_salary.toLocaleString()}</span>
                  </div>
                </div>

                <div className="mt-3">
                  <span className="text-[10px] text-slate-500 font-semibold block mb-1">Top Skills:</span>
                  <div className="flex flex-wrap gap-1">
                    {Object.keys(c.top_skills).slice(0, 3).map((sk, ski) => (
                      <span key={ski} className="text-[10px] bg-slate-800 text-indigo-300 px-1.5 py-0.5 rounded">{sk}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ----------------- 7. SKILL GAP ANALYSIS VIEW -----------------
function SkillGapView() {
  const [benchmarks, setBenchmarks] = useState({});
  const [selectedRole, setSelectedRole] = useState('Senior Data Scientist');
  const [employeeId, setEmployeeId] = useState('EMP0001');
  const [gapResult, setGapResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    fetch('/api/skills/benchmarks').then(r => r.json()).then(res => {
      setBenchmarks(res);
      if (Object.keys(res).length > 0) {
        setSelectedRole(Object.keys(res)[0]);
      }
    });
  }, []);

  const runGapAnalysis = async () => {
    setEvaluating(true);
    try {
      const res = await fetch('/api/skills/analyze-gap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_id: employeeId,
          target_role: selectedRole
        })
      });
      const data = await res.json();
      setGapResult(data);
    } catch (err) {
      console.error("Gap analysis failed:", err);
    } finally {
      setEvaluating(false);
    }
  };

  useEffect(() => {
    if (selectedRole && employeeId) {
      runGapAnalysis();
    }
  }, [selectedRole]);

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">Role Benchmark & Employee Skill Gap Analysis</h3>
        <p className="text-sm text-slate-400 mt-1">Algorithmic competency evaluation comparing employee skill sets against enterprise target benchmark roles.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <h4 className="font-semibold text-white text-sm">Select Candidate & Benchmark Role</h4>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Employee ID</label>
            <input
              type="text"
              value={employeeId}
              onChange={e => setEmployeeId(e.target.value.toUpperCase())}
              placeholder="e.g. EMP0001, EMP0012"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white uppercase font-mono"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Target Job Role Benchmark</label>
            <select
              value={selectedRole}
              onChange={e => setSelectedRole(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
            >
              {Object.keys(benchmarks).map(role => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          <button
            onClick={runGapAnalysis}
            disabled={evaluating}
            className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition"
          >
            {evaluating ? "Evaluating Skills..." : "Analyze Skill Gaps"}
          </button>
        </div>

        {/* Skill Gap Results Display */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl">
          {gapResult ? (
            <div className="space-y-5">
              <div className="flex justify-between items-start border-b border-slate-800 pb-4">
                <div>
                  <h4 className="text-lg font-bold text-white">{gapResult.candidate_name}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Current Role: <span className="text-slate-200">{gapResult.current_role}</span> → Target: <span className="text-indigo-400 font-semibold">{gapResult.target_role}</span></p>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-extrabold text-indigo-400">{gapResult.match_percentage}%</span>
                  <p className="text-[11px] text-slate-400">Benchmark Fit</p>
                </div>
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Readiness Status:</span>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {gapResult.readiness_status}
                </span>
              </div>

              {/* Matched vs Missing Skills Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h5 className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 mb-2">
                    <i data-lucide="check-circle-2" className="w-3.5 h-3.5"></i>
                    <span>Matched Core Skills ({gapResult.skills_summary.matched_core_skills.length})</span>
                  </h5>
                  <div className="flex flex-wrap gap-1.5">
                    {gapResult.skills_summary.matched_core_skills.map((s, i) => (
                      <span key={i} className="text-[11px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-0.5 rounded-md">{s}</span>
                    ))}
                    {gapResult.skills_summary.matched_core_skills.length === 0 && <span className="text-xs text-slate-500">None matched</span>}
                  </div>
                </div>

                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h5 className="text-xs font-semibold text-rose-400 flex items-center gap-1.5 mb-2">
                    <i data-lucide="x-circle" className="w-3.5 h-3.5"></i>
                    <span>Missing Core Skills ({gapResult.skills_summary.missing_core_skills.length})</span>
                  </h5>
                  <div className="flex flex-wrap gap-1.5">
                    {gapResult.skills_summary.missing_core_skills.map((s, i) => (
                      <span key={i} className="text-[11px] bg-rose-500/10 text-rose-300 border border-rose-500/20 px-2 py-0.5 rounded-md">{s}</span>
                    ))}
                    {gapResult.skills_summary.missing_core_skills.length === 0 && <span className="text-xs text-slate-500">All core skills fulfilled!</span>}
                  </div>
                </div>
              </div>

              {/* Recommended Training Pathway */}
              <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20">
                <h5 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">Recommended Upskilling Courses</h5>
                <div className="space-y-2">
                  {gapResult.recommended_trainings.map((course, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs">
                      <span className="text-slate-200 font-medium">• {course}</span>
                      <button className="text-[11px] text-indigo-400 hover:text-white px-2 py-0.5 bg-indigo-500/20 rounded border border-indigo-500/30 transition">Enroll</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-slate-500 text-xs">Enter an Employee ID to view skill gap analytics.</div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------- 8. AI RECOMMENDATIONS VIEW -----------------
function AIRecommendationsView() {
  const [requiredSkills, setRequiredSkills] = useState('Python, SQL, Machine Learning');
  const [minExp, setMinExp] = useState(2.0);
  const [teamSize, setTeamSize] = useState(3);
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const handleRecommend = async (e) => {
    e.preventDefault();
    setSearching(true);
    try {
      const skillsList = requiredSkills.split(',').map(s => s.strip ? s.strip() : s.trim()).filter(Boolean);
      const res = await fetch('/api/ai/recommend-team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          required_skills: skillsList,
          min_experience_years: Number(minExp),
          team_size: Number(teamSize)
        })
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Team recommendation failed:", err);
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    handleRecommend({ preventDefault: () => {} });
  }, []);

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-white">AI-Powered Project Team Matcher & Upskilling Roadmap</h3>
        <p className="text-sm text-slate-400 mt-1">Semantic skills-to-project optimization engine matching verified employee competencies.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Staffing Criteria */}
        <div className="glass-panel p-5 rounded-2xl">
          <h4 className="font-semibold text-white text-sm mb-4">Project Staffing Requirements</h4>
          <form onSubmit={handleRecommend} className="space-y-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Required Technical Skills (comma separated)</label>
              <input
                type="text"
                value={requiredSkills}
                onChange={e => setRequiredSkills(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white"
                placeholder="Python, SQL, React, AWS"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Min Experience: <span className="text-white font-bold">{minExp} yrs</span></label>
              <input
                type="range" min="0" max="15" step="0.5" value={minExp}
                onChange={e => setMinExp(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Team Size: <span className="text-white font-bold">{teamSize} Candidates</span></label>
              <input
                type="range" min="1" max="8" value={teamSize}
                onChange={e => setTeamSize(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={searching}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 text-white font-semibold shadow-md transition"
            >
              {searching ? "Matching Talent..." : "Find Best-Matched Staff"}
            </button>
          </form>
        </div>

        {/* Matched Team Results */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-semibold text-white text-base">Top Recommended Project Candidates</h4>
            {results && (
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full font-semibold">
                Avg Team Match: {results.team_readiness_score}%
              </span>
            )}
          </div>

          {results && results.selected_candidates ? (
            <div className="space-y-3">
              {results.selected_candidates.map((cand, idx) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-2">
                      <h5 className="font-bold text-white text-sm">{cand.name}</h5>
                      <span className="text-[10px] text-slate-400 font-mono">({cand.employee_id})</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{cand.job_role} • <span className="text-indigo-400">{cand.department}</span></p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {cand.all_technical_skills.slice(0, 4).map((sk, ski) => (
                        <span key={ski} className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">{sk}</span>
                      ))}
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xl font-bold text-emerald-400">{cand.match_percentage}%</span>
                    <p className="text-[10px] text-slate-400">Skill Match</p>
                    <p className="text-[10px] text-amber-400 font-semibold mt-1">★ {cand.performance_rating}/5.0</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20 text-slate-500 text-xs">No team candidates loaded yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

// ----------------- 9. RAG AI CHATBOT VIEW -----------------
function RAGChatbotView() {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "### Welcome to the AI Workforce Assistant\n\nI am connected directly to your enterprise workforce database and vector knowledge store. Ask me any question about headcount, common skills, staffing, skill gaps, or performance trends!"
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const sampleQuestions = [
    "Which department has the highest number of employees?",
    "What are the most common employee skills?",
    "Which employees have Python and SQL skills?",
    "Which skills are missing in the IT department?",
    "What training should employees receive?",
    "Which employees are suitable for a Data Analyst project?",
    "What are the workforce performance trends?"
  ];

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    const newMsgs = [...messages, { sender: 'user', text: q }];
    setMessages(newMsgs);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q })
      });
      const data = await res.json();
      setMessages([...newMsgs, {
        sender: 'assistant',
        text: data.answer,
        citations: data.citations
      }]);
    } catch (err) {
      setMessages([...newMsgs, {
        sender: 'assistant',
        text: "Error retrieving workforce intelligence. Please ensure backend services are active."
      }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="h-[calc(100vh-8.5rem)] flex flex-col glass-panel rounded-2xl overflow-hidden border border-slate-800">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-md">
            <i data-lucide="bot" className="w-5 h-5"></i>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Workforce RAG Assistant</h4>
            <p className="text-[10px] text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Grounded in Database & Vector Index
            </p>
          </div>
        </div>
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-4 py-2 border-b border-slate-800/60 bg-slate-900/20 flex gap-2 overflow-x-auto whitespace-nowrap text-xs">
        {sampleQuestions.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            className="px-3 py-1.5 rounded-full bg-slate-800/80 hover:bg-indigo-600 text-slate-300 hover:text-white border border-slate-700/60 transition flex-shrink-0 text-[11px]"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
              m.sender === 'user'
                ? 'bg-indigo-600 text-white rounded-br-none shadow-md'
                : 'glass-panel prose-dark text-slate-200 border border-slate-800/80 rounded-bl-none'
            }`}>
              {m.sender === 'assistant' ? (
                <div>
                  <div dangerouslySetInnerHTML={{ __html: window.marked ? window.marked.parse(m.text) : m.text }} />
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                      <span className="font-semibold text-slate-300">Grounding Sources: </span>
                      {m.citations.slice(0, 3).map(c => c.title).join(' • ')}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm">{m.text}</p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="glass-panel p-3 rounded-2xl border border-slate-800 text-xs text-indigo-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping"></span>
              Synthesizing response from workforce vector embeddings...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input bar */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/60">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask about workforce skills, departments, employee recommendations..."
            className="flex-1 bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold text-xs transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

// ----------------- 10. EMPLOYEE MANAGEMENT (CRUD) VIEW -----------------
function EmployeeCRUDView({ departments }) {
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');
  const [minExp, setMinExp] = useState('');
  const [maxExp, setMaxExp] = useState('');
  const [skillFilter, setSkillFilter] = useState('');
  const [page, setPage] = useState(0);
  const [limit] = useState(15);
  const [loading, setLoading] = useState(false);

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [currentEmp, setCurrentEmp] = useState(null);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: page * limit,
        limit: limit
      });
      if (search) params.append('search', search);
      if (deptFilter && deptFilter !== 'All') params.append('department', deptFilter);
      if (minExp) params.append('min_exp', minExp);
      if (maxExp) params.append('max_exp', maxExp);
      if (skillFilter) params.append('skill', skillFilter);

      const res = await fetch(`/api/employees?${params.toString()}`);
      const data = await res.json();
      setEmployees(data.employees || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to fetch employees:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [page, deptFilter, minExp, maxExp, skillFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchEmployees();
  };

  const handleDelete = async (empId) => {
    if (!confirm(`Are you sure you want to delete employee ${empId}? This will remove all their skills and records.`)) return;
    try {
      const res = await fetch(`/api/employees/${empId}`, { method: 'DELETE' });
      if (res.ok) {
        fetchEmployees();
      }
    } catch (err) {
      alert("Failed to delete employee: " + err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h3 className="text-lg font-bold text-white">Employee Management (CRUD Operations)</h3>
          <p className="text-xs text-slate-400">Total {total} database records with normalized multi-value skills.</p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition"
          >
            <i data-lucide="plus" className="w-4 h-4"></i>
            <span>Add Employee</span>
          </button>
          <a
            href="/api/employees/export/csv"
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition"
          >
            <i data-lucide="file-spreadsheet" className="w-4 h-4"></i>
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-2xl grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
        <form onSubmit={handleSearchSubmit} className="lg:col-span-2 flex gap-2">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by name, ID, or job role..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white"
          />
          <button type="submit" className="px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg">Search</button>
        </form>

        <select
          value={deptFilter}
          onChange={e => { setDeptFilter(e.target.value); setPage(0); }}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white"
        >
          <option value="All">All Departments</option>
          {departments.map(d => (
            <option key={d.id} value={d.name}>{d.name}</option>
          ))}
        </select>

        <input
          type="text"
          value={skillFilter}
          onChange={e => { setSkillFilter(e.target.value); setPage(0); }}
          placeholder="Filter by skill (e.g. Python)"
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white"
        />

        <div className="flex gap-2">
          <input
            type="number"
            value={minExp}
            onChange={e => { setMinExp(e.target.value); setPage(0); }}
            placeholder="Min Exp"
            className="w-1/2 bg-slate-900 border border-slate-700 rounded-lg px-2 py-2 text-white"
          />
          <input
            type="number"
            value={maxExp}
            onChange={e => { setMaxExp(e.target.value); setPage(0); }}
            placeholder="Max Exp"
            className="w-1/2 bg-slate-900 border border-slate-700 rounded-lg px-2 py-2 text-white"
          />
        </div>
      </div>

      {/* Employees Data Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3.5">Employee ID</th>
                <th className="p-3.5">Name</th>
                <th className="p-3.5">Department</th>
                <th className="p-3.5">Job Role</th>
                <th className="p-3.5">Exp (Yrs)</th>
                <th className="p-3.5">Salary</th>
                <th className="p-3.5">Performance</th>
                <th className="p-3.5">Key Skills</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {employees.map((emp) => (
                <tr key={emp.employee_id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3.5 font-mono text-indigo-400 font-semibold">{emp.employee_id}</td>
                  <td className="p-3.5 font-medium text-white">{emp.name}</td>
                  <td className="p-3.5 text-slate-300">{emp.department}</td>
                  <td className="p-3.5 text-slate-300">{emp.job_role}</td>
                  <td className="p-3.5 text-slate-300">{emp.experience_years}</td>
                  <td className="p-3.5 font-mono text-emerald-400">${Number(emp.salary).toLocaleString()}</td>
                  <td className="p-3.5 text-amber-400 font-semibold">★ {emp.performance_rating}</td>
                  <td className="p-3.5 text-slate-400 max-w-[200px] truncate">{emp.top_skills || "General"}</td>
                  <td className="p-3.5 text-right space-x-1">
                    <button
                      onClick={() => { setCurrentEmp(emp); setIsEditModalOpen(true); }}
                      className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded transition"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(emp.employee_id)}
                      className="px-2 py-1 bg-rose-500/10 hover:bg-rose-500 text-rose-300 hover:text-white rounded border border-rose-500/20 transition"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {employees.length === 0 && !loading && (
                <tr>
                  <td colSpan="9" className="text-center py-12 text-slate-500">No employee records match the filter criteria.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/40 flex justify-between items-center text-xs text-slate-400">
          <span>Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total} employees</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded text-white"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= total}
              className="px-3 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 rounded text-white"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Add Employee Modal */}
      {isAddModalOpen && (
        <AddEmployeeModal
          departments={departments}
          onClose={() => setIsAddModalOpen(false)}
          onSuccess={() => { setIsAddModalOpen(false); fetchEmployees(); }}
        />
      )}

      {/* Edit Employee Modal */}
      {isEditModalOpen && currentEmp && (
        <EditEmployeeModal
          employee={currentEmp}
          departments={departments}
          onClose={() => setIsEditModalOpen(false)}
          onSuccess={() => { setIsEditModalOpen(false); fetchEmployees(); }}
        />
      )}
    </div>
  );
}

// Modal for Adding Employee
function AddEmployeeModal({ departments, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    age: 28,
    gender: 'Female',
    department_name: 'Engineering',
    job_role: 'Software Engineer',
    experience_years: 3.5,
    salary: 95000,
    education: "Bachelor's Degree",
    location: 'Remote',
    technical_skills: 'Python, SQL, React',
    soft_skills: 'Communication, Teamwork',
    performance_rating: 3.8,
    overtime: 'No'
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...formData,
        technical_skills: formData.technical_skills.split(',').map(s => s.trim()).filter(Boolean),
        soft_skills: formData.soft_skills.split(',').map(s => s.trim()).filter(Boolean)
      };
      const res = await fetch('/api/employees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        onSuccess();
      } else {
        const err = await res.json();
        alert("Failed to create employee: " + (err.detail || "Validation error"));
      }
    } catch (err) {
      alert("Error: " + err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="glass-panel bg-[#0f172a] border border-slate-700 p-6 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h4 className="text-base font-bold text-white">Add New Employee</h4>
          <button onClick={onClose} className="text-slate-400 hover:text-white">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="text-slate-400 block mb-1">Full Name</label>
            <input required type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-slate-400 block mb-1">Department</label>
              <select value={formData.department_name} onChange={e => setFormData({...formData, department_name: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white">
                {departments.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Job Role</label>
              <input required type="text" value={formData.job_role} onChange={e => setFormData({...formData, job_role: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-slate-400 block mb-1">Age</label>
              <input type="number" value={formData.age} onChange={e => setFormData({...formData, age: Number(e.target.value)})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Exp (Years)</label>
              <input type="number" step="0.5" value={formData.experience_years} onChange={e => setFormData({...formData, experience_years: Number(e.target.value)})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Salary ($)</label>
              <input type="number" value={formData.salary} onChange={e => setFormData({...formData, salary: Number(e.target.value)})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Technical Skills (comma-separated)</label>
            <input type="text" value={formData.technical_skills} onChange={e => setFormData({...formData, technical_skills: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" placeholder="Python, SQL, React, AWS" />
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Soft Skills (comma-separated)</label>
            <input type="text" value={formData.soft_skills} onChange={e => setFormData({...formData, soft_skills: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
          </div>

          <div className="flex justify-end gap-2 pt-3">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold">{submitting ? "Saving..." : "Save Employee"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Modal for Editing Employee
function EditEmployeeModal({ employee, departments, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: employee.name,
    salary: employee.salary,
    job_role: employee.job_role,
    performance_rating: employee.performance_rating,
    experience_years: employee.experience_years
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch(`/api/employees/${employee.employee_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        onSuccess();
      } else {
        alert("Failed to update employee");
      }
    } catch (err) {
      alert("Error: " + err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="glass-panel bg-[#0f172a] border border-slate-700 p-6 rounded-2xl max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h4 className="text-base font-bold text-white">Edit Employee ({employee.employee_id})</h4>
          <button onClick={onClose} className="text-slate-400 hover:text-white">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="text-slate-400 block mb-1">Full Name</label>
            <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Job Role</label>
            <input type="text" value={formData.job_role} onChange={e => setFormData({...formData, job_role: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-slate-400 block mb-1">Salary ($)</label>
              <input type="number" value={formData.salary} onChange={e => setFormData({...formData, salary: Number(e.target.value)})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Performance (1-5)</label>
              <input type="number" step="0.1" value={formData.performance_rating} onChange={e => setFormData({...formData, performance_rating: Number(e.target.value)})} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white" />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300">Cancel</button>
            <button type="submit" disabled={saving} className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold">{saving ? "Updating..." : "Save Changes"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Mount the React Application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
