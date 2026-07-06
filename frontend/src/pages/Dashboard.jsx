import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Plus, Briefcase, Calendar, ChevronRight, Layers, X, AlertCircle, Trash2 } from 'lucide-react';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    client: '',
    global_margin_pct: 0.15,
    global_erection_pct: 0.10,
    default_annual_escalation_pct: 0.045,
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [projRes, catRes] = await Promise.all([
        api.get('/projects'),
        api.get('/categories'),
      ]);
      setProjects(projRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    setError('');
    setCreating(true);
    try {
      await api.post('/projects', {
        ...newProject,
        global_margin_pct: parseFloat(newProject.global_margin_pct),
        global_erection_pct: parseFloat(newProject.global_erection_pct),
        default_annual_escalation_pct: parseFloat(newProject.default_annual_escalation_pct),
      });
      setIsModalOpen(false);
      setNewProject({
        name: '',
        client: '',
        global_margin_pct: 0.15,
        global_erection_pct: 0.10,
        default_annual_escalation_pct: 0.045,
      });
      fetchDashboardData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteProject = async (e, projectId, projectName) => {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to permanently delete project "${projectName}" and all its equipment records?`)) {
      try {
        await api.delete(`/projects/${projectId}`);
        fetchDashboardData();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete project.');
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-6 transition-all duration-300">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Estimation Projects
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Select or initialize a project
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-primary py-2 px-4 text-xs font-semibold cursor-pointer transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 gap-4 max-w-md">
        <div className="glass-panel p-4 flex items-center justify-between">
          <div>
            <div className="text-[11px] text-slate-400 font-medium">Workspaces</div>
            <div className="text-xl font-bold text-white mt-0.5">{projects.length}</div>
          </div>
          <Briefcase className="w-5 h-5 text-cyan-400" />
        </div>
        <div className="glass-panel p-4 flex items-center justify-between">
          <div>
            <div className="text-[11px] text-slate-400 font-medium">Categories Configured</div>
            <div className="text-xl font-bold text-white mt-0.5">{categories.length}</div>
          </div>
          <Layers className="w-5 h-5 text-blue-400" />
        </div>
      </div>

      {/* Projects List */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-xs font-mono">Loading estimation projects...</div>
      ) : projects.length === 0 ? (
        <div className="glass-panel p-12 text-center space-y-3">
          <div className="text-sm font-semibold text-slate-300">No projects configured</div>
          <button onClick={() => setIsModalOpen(true)} className="btn-primary mt-2 text-xs">
            Create First Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="glass-panel p-5 flex flex-col justify-between hover:border-cyan-500/40 transition-all group relative"
            >
              <Link to={`/projects/${project.id}`} className="flex-1 block">
                <div className="flex items-start justify-between gap-3 pr-6">
                  <h3 className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors line-clamp-1">
                    {project.name}
                  </h3>
                  <span className="text-[10px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    #{project.id}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Client: <strong className="text-slate-300">{project.client}</strong>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-4 p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-center font-mono">
                  <div>
                    <div className="text-[10px] uppercase text-slate-300 font-semibold font-sans">Margin</div>
                    <div className="text-xs font-bold text-slate-200 mt-0.5">
                      {(project.global_margin_pct * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="border-x border-slate-800">
                    <div className="text-[10px] uppercase text-slate-300 font-semibold font-sans">Erection</div>
                    <div className="text-xs font-bold text-slate-200 mt-0.5">
                      {(project.global_erection_pct * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase text-slate-300 font-semibold font-sans">Escalation</div>
                    <div className="text-xs font-bold text-cyan-400 mt-0.5">
                      {(project.default_annual_escalation_pct * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </Link>

              {/* Absolute Delete Button on Card Top Right */}
              <button
                onClick={(e) => handleDeleteProject(e, project.id, project.name)}
                className="absolute top-4 right-4 text-slate-400 hover:text-red-400 transition-colors cursor-pointer p-1"
                title="Delete Project Workspace"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>

              <Link to={`/projects/${project.id}`} className="flex items-center justify-between pt-4 mt-4 border-t border-slate-800/60 text-xs text-slate-300 block">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(project.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                </span>
                <span className="flex items-center gap-1 font-semibold text-cyan-400 group-hover:translate-x-1 transition-transform">
                  Enter <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* New Project Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="glass-panel max-w-md w-full p-6 relative bg-slate-900 border border-slate-700">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>

            <h3 className="text-base font-bold text-white mb-4">New Project Workspace</h3>

            <form onSubmit={handleCreateProject} className="space-y-4">
              {error && (
                <div className="p-2.5 rounded bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  required
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="e.g. GP-II"
                  className="input-field text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Client Name
                </label>
                <input
                  type="text"
                  required
                  value={newProject.client}
                  onChange={(e) => setNewProject({ ...newProject, client: e.target.value })}
                  placeholder="e.g. Client_X_India"
                  className="input-field text-xs"
                />
              </div>

              <div className="grid grid-cols-3 gap-2 pt-1">
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">Margin (0.15)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newProject.global_margin_pct}
                    onChange={(e) => setNewProject({ ...newProject, global_margin_pct: e.target.value })}
                    className="input-field text-xs py-1.5"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">Erection (0.10)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newProject.global_erection_pct}
                    onChange={(e) => setNewProject({ ...newProject, global_erection_pct: e.target.value })}
                    className="input-field text-xs py-1.5"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">Escalation (0.045)</label>
                  <input
                    type="number"
                    step="0.005"
                    required
                    value={newProject.default_annual_escalation_pct}
                    onChange={(e) => setNewProject({ ...newProject, default_annual_escalation_pct: e.target.value })}
                    className="input-field text-xs py-1.5"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-800 mt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="btn-secondary text-xs py-1.5 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="btn-primary text-xs py-1.5 cursor-pointer"
                >
                  {creating ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
