import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowRight, CalendarCheck, ClipboardList, LayoutDashboard,
  LogOut, Menu, Plus, Search, Settings2, Trash2, Users, X,
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const today = new Date().toISOString().slice(0, 10);

async function request(path, options = {}) {
  const token = localStorage.getItem("access");
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (response.status === 401) {
    localStorage.clear();
    window.location.reload();
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || Object.values(body).flat().join(" ") || "Something went wrong");
  }
  return response.status === 204 ? null : response.json();
}

const list = (data) => data?.results || data || [];

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    try {
      const data = await request("/auth/login/", { method: "POST", body: JSON.stringify({ username, password }) });
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      onLogin();
    } catch (err) { setError(err.message); }
  }
  return <main className="auth-shell"><section className="auth-card">
    <div className="brand-mark">A</div><p className="eyebrow">Attendance management</p>
    <h1>Welcome back</h1><p className="muted">Sign in to keep your team on track.</p>
    <form onSubmit={submit} className="stack">
      <label>Username<input required value={username} onChange={(e) => setUsername(e.target.value)} placeholder="e.g. jane.doe" /></label>
      <label>Password<input required type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Your password" /></label>
      {error && <p className="error">{error}</p>}<button className="button primary" type="submit">Sign in <ArrowRight size={17} /></button>
    </form>
  </section></main>;
}

function App() {
  const [loggedIn, setLoggedIn] = useState(Boolean(localStorage.getItem("access")));
  if (!loggedIn) return <Login onLogin={() => setLoggedIn(true)} />;
  return <Dashboard onLogout={() => { localStorage.clear(); setLoggedIn(false); }} />;
}

function Dashboard({ onLogout }) {
  const [section, setSection] = useState("Overview");
  const [menuOpen, setMenuOpen] = useState(false);
  const [data, setData] = useState({ attendance: [], members: [], departments: [] });
  const [error, setError] = useState("");
  const reload = () => Promise.all([request("/attendance/"), request("/members/"), request("/departments/")])
    .then(([attendance, members, departments]) => setData({ attendance: list(attendance), members: list(members), departments: list(departments) }))
    .catch((err) => setError(err.message));
  useEffect(() => { reload(); }, []);
  const nav = [["Overview", LayoutDashboard], ["Attendance", CalendarCheck], ["People", Users]];
  return <div className="app-shell">
    <aside className={menuOpen ? "sidebar open" : "sidebar"}>
      <div className="sidebar-head"><div className="brand-mark small">A</div><strong>Attendly</strong><button className="icon-button mobile-only" onClick={() => setMenuOpen(false)}><X size={18} /></button></div>
      <p className="nav-label">Workspace</p>{nav.map(([name, Icon]) => <button className={section === name ? "nav-item active" : "nav-item"} key={name} onClick={() => { setSection(name); setMenuOpen(false); }}><Icon size={18} />{name}</button>)}
      <div className="sidebar-bottom"><button className="nav-item"><Settings2 size={18} />Settings</button><button className="nav-item" onClick={onLogout}><LogOut size={18} />Sign out</button></div>
    </aside>
    <main className="main-content"><header className="topbar"><button className="icon-button mobile-only" onClick={() => setMenuOpen(true)}><Menu size={21} /></button><div><p className="eyebrow">{new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}</p><h2>{section}</h2></div><div className="avatar">A</div></header>
      {error && <div className="alert">{error}<button onClick={() => setError("")}><X size={15} /></button></div>}
      <section className="content">{section === "Overview" && <Overview data={data} />}
        {section === "Attendance" && <AttendancePage data={data} reload={reload} setError={setError} />}
        {section === "People" && <PeoplePage data={data} reload={reload} setError={setError} />}
      </section>
    </main>
  </div>;
}

function Overview({ data }) {
  const present = data.attendance.filter((item) => item.status === "present").length;
  const recent = data.attendance.slice(0, 8);
  return <><div className="welcome"><div><p className="eyebrow">Your workspace</p><h1>Good morning, Admin <span>✦</span></h1><p className="muted">Here’s what’s happening with attendance today.</p></div><div className="date-pill"><CalendarCheck size={17} /> {today}</div></div>
    <div className="stats"><Stat icon={<Users />} label="Total members" value={data.members.length} tone="purple" /><Stat icon={<CalendarCheck />} label="Present today" value={present} tone="green" /><Stat icon={<Activity />} label="Attendance rate" value={data.attendance.length ? `${Math.round((present / data.attendance.length) * 100)}%` : "0%"} tone="orange" /><Stat icon={<ClipboardList />} label="Departments" value={data.departments.length} tone="blue" /></div>
    <RecordTable records={recent} title="Recent attendance" description="Latest attendance records across your workspace." /></>;
}

function AttendancePage({ data, reload, setError }) {
  const [query, setQuery] = useState("");
  const [form, setForm] = useState({ member: "", date: today, status: "present" });
  const filtered = useMemo(() => data.attendance.filter((item) => `${item.member_name} ${item.date} ${item.status}`.toLowerCase().includes(query.toLowerCase())), [data.attendance, query]);
  async function save(event) {
    event.preventDefault();
    try { await request("/attendance/", { method: "POST", body: JSON.stringify({ ...form, member: Number(form.member) }) }); setForm({ member: "", date: today, status: "present" }); await reload(); }
    catch (err) { setError(err.message); }
  }
  return <><PageIntro title="Attendance records" text="Mark and review daily attendance." /><section className="panel form-panel"><form className="inline-form" onSubmit={save}><select required value={form.member} onChange={(e) => setForm({ ...form, member: e.target.value })}><option value="">Select member</option>{data.members.map((member) => <option value={member.id} key={member.id}>{member.employee_id} · {member.username}</option>)}</select><input required type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} /><select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option value="present">Present</option><option value="absent">Absent</option><option value="leave">Leave</option></select><button className="button primary" type="submit"><Plus size={16} />Mark attendance</button></form></section>
    <section className="panel"><div className="panel-head"><div><h3>All records</h3><p className="muted">{data.attendance.length} records</p></div><div className="search"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search records..." /></div></div><RecordRows records={filtered} /></section></>;
}

function PeoplePage({ data, reload, setError }) {
  const [name, setName] = useState("");
  async function addDepartment(event) {
    event.preventDefault();
    try { await request("/departments/", { method: "POST", body: JSON.stringify({ name }) }); setName(""); await reload(); }
    catch (err) { setError(err.message); }
  }
  return <><PageIntro title="People" text="Manage departments and view your members." /><div className="people-grid"><section className="panel"><div className="panel-head"><div><h3>Departments</h3><p className="muted">{data.departments.length} departments</p></div></div><form className="inline-form compact" onSubmit={addDepartment}><input required value={name} onChange={(e) => setName(e.target.value)} placeholder="New department name" /><button className="button primary" type="submit"><Plus size={16} />Add</button></form><div className="list">{data.departments.map((department) => <div className="list-row" key={department.id}><span className="avatar muted-avatar">{department.name[0]}</span><strong>{department.name}</strong><span className="muted">{data.members.filter((member) => member.department === department.id).length} members</span></div>)}</div></section><section className="panel"><div className="panel-head"><div><h3>Members</h3><p className="muted">Directory of registered members.</p></div></div><div className="list">{data.members.map((member) => <div className="list-row" key={member.id}><span className="avatar muted-avatar">{(member.username || "?")[0].toUpperCase()}</span><div><strong>{member.username}</strong><small>{member.employee_id}</small></div><span className="muted">{data.departments.find((d) => d.id === member.department)?.name || "Unassigned"}</span></div>)}</div></section></div></>;
}

function PageIntro({ title, text }) { return <div className="page-intro"><div><p className="eyebrow">Workspace</p><h1>{title}</h1><p className="muted">{text}</p></div></div>; }
function RecordTable({ records, title, description }) { return <section className="panel"><div className="panel-head"><div><h3>{title}</h3><p className="muted">{description}</p></div></div><RecordRows records={records} /></section>; }
function RecordRows({ records }) { return <div className="table-wrap"><table><thead><tr><th>Member</th><th>Date</th><th>Status</th><th>Marked by</th></tr></thead><tbody>{records.map((item) => <tr key={item.id}><td><div className="person"><span className="avatar muted-avatar">{(item.member_name || "?")[0].toUpperCase()}</span><strong>{item.member_name || "Unknown member"}</strong></div></td><td>{item.date}</td><td><span className={`status ${item.status}`}>{item.status}</span></td><td>Admin</td></tr>)}{!records.length && <tr><td colSpan="4" className="empty">No attendance records found.</td></tr>}</tbody></table></div>; }
function Stat({ icon, label, value, tone }) { return <div className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><div><p className="muted">{label}</p><strong>{value}</strong></div></div>; }
createRoot(document.getElementById("root")).render(<App />);
