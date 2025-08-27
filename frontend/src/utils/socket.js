// frontend/src/utils/socket.js
import io from 'socket.io-client';

const API_KEY = process.env.REACT_APP_API_KEY || 'demo-key-123';

// For Django WebSocket, we'll use native WebSocket instead of socket.io
class DjangoWebSocketClient {
  constructor(url, apiKey) {
    this.url = `${url}?api_key=${apiKey}`;
    this.callbacks = {};
  }

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      if (this.callbacks.connect) this.callbacks.connect();
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (this.callbacks[data.type]) {
        this.callbacks[data.type](data.data);
      }
    };
    
    this.ws.onerror = (error) => {
      if (this.callbacks.error) this.callbacks.error(error);
    };
    
    this.ws.onclose = () => {
      if (this.callbacks.disconnect) this.callbacks.disconnect();
    };
  }

  on(event, callback) {
    this.callbacks[event] = callback;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const createWebSocketConnection = () => {
  return new DjangoWebSocketClient('ws://localhost:8000/ws/orders/', API_KEY);
};