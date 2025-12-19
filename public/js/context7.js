// context7.js - 前后端数据交互框架
class Context7 {
    constructor() {
        this.context = {};
        this.listeners = {};
    }
    
    // 设置上下文数据
    set(key, value) {
        this.context[key] = value;
        this.notify(key, value);
    }
    
    // 获取上下文数据
    get(key) {
        return this.context[key];
    }
    
    // 删除上下文数据
    remove(key) {
        if (this.context.hasOwnProperty(key)) {
            delete this.context[key];
            this.notify(key, undefined);
        }
    }
    
    // 监听数据变化
    on(key, callback) {
        if (!this.listeners[key]) {
            this.listeners[key] = [];
        }
        this.listeners[key].push(callback);
        
        // 返回取消监听的函数
        return () => {
            this.listeners[key] = this.listeners[key].filter(cb => cb !== callback);
        };
    }
    
    // 通知监听器数据变化
    notify(key, value) {
        if (this.listeners[key]) {
            this.listeners[key].forEach(callback => {
                try {
                    callback(value);
                } catch (error) {
                    console.error('Context7 listener error:', error);
                }
            });
        }
    }
    
    // 发送HTTP请求
    async request(url, options = {}) {
        try {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json'
                },
                ...options
            };
            
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Context7 request error:', error);
            throw error;
        }
    }
    
    // 发送POST请求
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // 发送GET请求
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, {
            method: 'GET'
        });
    }
}

// 创建全局实例
window.context7 = new Context7();
