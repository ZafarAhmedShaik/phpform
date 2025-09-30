import React, { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('admin_token'));

  useEffect(() => {
    if (token) {
      setIsAuthenticated(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const login = (newToken) => {
    localStorage.setItem('admin_token', newToken);
    setToken(newToken);
    setIsAuthenticated(true);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
    setIsAuthenticated(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Header = () => {
  const { isAuthenticated, logout } = useAuth();
  
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold hover:text-blue-200 transition-colors">
              Client Portal
            </Link>
            <Link to="/" className="hover:text-blue-200 transition-colors">
              Submit Form
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/admin" className="hover:text-blue-200 transition-colors">
                  Admin Dashboard
                </Link>
                <button 
                  onClick={logout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-md transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link to="/admin/login" className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-md transition-colors">
                Admin Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

const ClientForm = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone_number: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.full_name.trim() || formData.full_name.length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters long';
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    const phoneRegex = /^[+]?[0-9\s\-\(\)]{10,20}$/;
    if (!phoneRegex.test(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number (10-20 digits)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setMessage('');
    
    try {
      await axios.post(`${API}/clients`, formData);
      setMessage('Thank you! Your information has been submitted successfully.');
      setFormData({ full_name: '', email: '', phone_number: '' });
    } catch (error) {
      if (error.response?.data?.detail) {
        setMessage(`Error: ${error.response.data.detail}`);
      } else {
        setMessage('An error occurred. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Client Information</h1>
          <p className="text-gray-600">Please fill out your details below</p>
        </div>
        
        {message && (
          <div className={`mb-6 p-4 rounded-md ${message.includes('Error') 
            ? 'bg-red-50 text-red-700 border border-red-200' 
            : 'bg-green-50 text-green-700 border border-green-200'
          }`}>
            {message}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className={`w-full px-4 py-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                errors.full_name ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Enter your full name"
              required
            />
            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">{errors.full_name}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                errors.email ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Enter your email address"
              required
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>
          
          <div>
            <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number *
            </label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              className={`w-full px-4 py-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                errors.phone_number ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Enter your phone number"
              required
            />
            {errors.phone_number && (
              <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Information'}
          </button>
        </form>
        
        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          Your information is secure and will only be used for administrative purposes.
        </div>
      </div>
    </div>
  );
};

const AdminLogin = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLogging, setIsLogging] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLogging(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/admin/login`, credentials);
      login(response.data.access_token);
      navigate('/admin');
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsLogging(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100 py-12 px-4">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Admin Login</h1>
          <p className="text-gray-600">Access the admin dashboard</p>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-md">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              placeholder="Enter admin username"
              required
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              placeholder="Enter admin password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLogging}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isLogging ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          <p><strong>Demo Credentials:</strong></p>
          <p>Username: admin</p>
          <p>Password: admin123</p>
        </div>
      </div>
    </div>
  );
};

const AdminDashboard = () => {
  const [clients, setClients] = useState([]);
  const [stats, setStats] = useState({ total_clients: 0, recent_submissions: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [clientsRes, statsRes] = await Promise.all([
        axios.get(`${API}/admin/clients`),
        axios.get(`${API}/admin/stats`)
      ]);
      
      setClients(clientsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.get(`${API}/admin/clients/export`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'client_submissions.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError('Failed to export data');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage client submissions and export data</p>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-md">
            {error}
          </div>
        )}
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Clients</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.total_clients}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Recent Submissions</h3>
            <p className="text-3xl font-bold text-green-600">{stats.recent_submissions}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 flex items-center justify-center">
            <button
              onClick={handleExport}
              disabled={exporting}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {exporting ? 'Exporting...' : 'Export CSV'}
            </button>
          </div>
        </div>
        
        {/* Client Data Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">Client Submissions</h2>
          </div>
          
          {clients.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <p>No client submissions yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Full Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted At
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {clients.map((client) => (
                    <tr key={client.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {client.full_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {client.phone_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(client.submitted_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/admin/login" />;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<ClientForm />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;