import React from 'react';
import { AlertCircle, RefreshCw } from 'react-icons/fa';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center p-6">
          <div className="max-w-md bg-gray-900 border border-gray-700 rounded-lg p-8 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="text-red-400" size={32} />
              <h1 className="text-2xl font-bold text-gray-100">Something Went Wrong</h1>
            </div>
            
            <p className="text-gray-400 mb-4">
              We encountered an unexpected error. Please try refreshing the page or return to the dashboard.
            </p>

            {this.state.error && (
              <div className="bg-gray-800 rounded p-3 mb-4 border border-gray-700">
                <p className="text-xs text-gray-300 font-mono break-words">
                  {this.state.error.toString()}
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={this.handleReset}
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-semibold transition"
              >
                <RefreshCw size={16} /> Go Home
              </button>
              <button
                onClick={() => window.location.reload()}
                className="flex-1 flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 px-4 py-2 rounded font-semibold transition"
              >
                <RefreshCw size={16} /> Refresh
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
