/**
 * API Service - Comprehensive backend integration
 * Connects Kendo React UI with all backend systems
 */

class ApiService {
    constructor() {
        // Updated to point to v1 API by default
        this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');

        // Request interceptor for adding auth headers
        this.setupInterceptors();
    }

    setupInterceptors() {
        // Add default headers
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (this.token) {
            this.defaultHeaders['Authorization'] = `Bearer ${this.token}`;
        }
    }

    async request(method, endpoint, data = null, customHeaders = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = { ...this.defaultHeaders, ...customHeaders };

        const config = {
            method,
            headers,
            body: data ? JSON.stringify(data) : null
        };

        try {
            const response = await fetch(url, config);
            const result = await response.json();

            if (response.status === 401 && this.refreshToken) {
                // Try to refresh token
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry original request
                    headers['Authorization'] = `Bearer ${this.token}`;
                    const retryResponse = await fetch(url, { ...config, headers });
                    return await retryResponse.json();
                }
            }

            return result;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Authentication Methods
    async login(username, password) {
        const response = await this.request('POST', '/auth/login', {
            username,
            password
        });

        if (response.success && response.data) {
            this.token = response.data.access_token;
            this.refreshToken = response.data.refresh_token;

            localStorage.setItem('access_token', this.token);
            localStorage.setItem('refresh_token', this.refreshToken);
            localStorage.setItem('user', JSON.stringify(response.data.user));

            this.setupInterceptors();
        }

        return response;
    }

    async register(username, email, password) {
        return await this.request('POST', '/auth/register', {
            username,
            email,
            password
        });
    }

    async logout() {
        const response = await this.request('POST', '/auth/logout');

        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');

        this.setupInterceptors();
        return response;
    }

    async refreshAccessToken() {
        try {
            const response = await this.request('POST', '/auth/refresh', {
                refresh_token: this.refreshToken
            });

            if (response.success && response.data) {
                this.token = response.data.access_token;
                localStorage.setItem('access_token', this.token);
                this.setupInterceptors();
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
        return false;
    }

    async getProfile() {
        return await this.request('GET', '/auth/me');
    }

    // Portfolio Methods
    async getPortfolioData() {
        return await this.request('GET', '/api/portfolio/data');
    }

    async getPortfolioPerformance() {
        return await this.request('GET', '/api/portfolio/performance');
    }

    async getPortfolioHistory() {
        return await this.request('GET', '/api/portfolio/history');
    }

    // Betting Methods
    async getBettingOpportunities() {
        return await this.request('GET', '/api/betting/opportunities');
    }

    async placeBet(opportunityId, amount, selection) {
        return await this.request('POST', '/api/betting/place', {
            opportunity_id: opportunityId,
            amount,
            selection
        });
    }

    async getBettingHistory() {
        return await this.request('GET', '/api/betting/history');
    }

    // Analytics Methods
    async getAnalyticsDashboard() {
        return await this.request('GET', '/api/analytics/dashboard');
    }

    async getSportsAnalytics() {
        return await this.request('GET', '/api/analytics/sports');
    }

    async getROIAnalytics() {
        return await this.request('GET', '/api/analytics/roi');
    }

    // Payment Methods
    async getPaymentMethods() {
        return await this.request('GET', '/api/payments/methods');
    }

    async processPayment(amount, description, paymentMethodId, gateway = 'stripe') {
        return await this.request('POST', '/api/payments/process', {
            amount,
            description,
            payment_method_id: paymentMethodId,
            gateway
        });
    }

    // Subscription Methods
    async getSubscriptionTiers() {
        return await this.request('GET', '/api/subscription/tiers');
    }

    async upgradeSubscription(tierId, paymentMethodId) {
        return await this.request('POST', '/api/subscription/upgrade', {
            tier_id: tierId,
            payment_method_id: paymentMethodId
        });
    }

    // Admin Methods
    async getAdminUsers() {
        return await this.request('GET', '/api/admin/users');
    }

    async updateUser(userId, updates) {
        return await this.request('PUT', '/api/admin/users/update', {
            user_id: userId,
            updates
        });
    }

    async getSystemHealth() {
        return await this.request('GET', '/api/admin/system/health');
    }

    // System Methods
    async getSystemStatus() {
        return await this.request('GET', '/api/system/status');
    }

    async getSystemMetrics() {
        return await this.request('GET', '/api/system/metrics');
    }

    // Real-time Methods
    async connectRealtime() {
        return await this.request('POST', '/api/realtime/connect');
    }

    async subscribeRealtime(connectionId, dataTypes) {
        return await this.request('POST', '/api/realtime/subscribe', {
            connection_id: connectionId,
            data_types: dataTypes
        });
    }

    // AI Prediction Methods (for Parlay Maker)
    async getPrediction(sports, queryText, options = {}) {
        const user = this.getCurrentUser();
        return await this.request('POST', '/predict', {
            user_id: user?.id || 'anonymous',
            sports: sports,
            query_text: queryText,
            ...options
        });
    }

    // Utility Methods
    isAuthenticated() {
        return !!this.token;
    }

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    // WebSocket connection for real-time updates
    connectWebSocket(onMessage, onError = null, onClose = null) {
        if (!this.isAuthenticated()) {
            console.error('Must be authenticated to connect WebSocket');
            return null;
        }

        const wsUrl = this.baseURL.replace('http', 'ws') + '/ws';
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('✅ WebSocket connected');
            // Send authentication
            ws.send(JSON.stringify({
                type: 'authenticate',
                token: this.token
            }));
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (onError) onError(error);
        };

        ws.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason);
            if (onClose) onClose(event);
        };

        return ws;
    }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService; 