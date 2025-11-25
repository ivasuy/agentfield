import WebSocket from 'ws';
import type { MemoryChangeEvent } from './MemoryInterface.js';

export type MemoryEventHandler = (event: MemoryChangeEvent) => Promise<void> | void;

export class MemoryEventClient {
  private readonly url: string;
  private ws?: WebSocket;
  private handlers: MemoryEventHandler[] = [];
  private reconnectDelay = 1000;
  private closed = false;

  constructor(baseUrl: string) {
    this.url = `${baseUrl.replace(/^http/, 'ws')}/api/v1/memory/events/ws`;
  }

  start() {
    if (this.ws) return;
    this.connect();
  }

  onEvent(handler: MemoryEventHandler) {
    this.handlers.push(handler);
  }

  stop() {
    this.closed = true;
    this.ws?.close();
  }

  private connect() {
    this.ws = new WebSocket(this.url);

    this.ws.on('open', () => {
      this.reconnectDelay = 1000;
    });

    this.ws.on('message', async (raw) => {
      try {
        const parsed = JSON.parse(raw.toString()) as MemoryChangeEvent;
        for (const handler of this.handlers) {
          await handler(parsed);
        }
      } catch (err) {
        // swallow parsing errors to keep connection alive
        console.error('Failed to handle memory event', err);
      }
    });

    this.ws.on('close', () => this.scheduleReconnect());
    this.ws.on('error', () => this.scheduleReconnect());
  }

  private scheduleReconnect() {
    if (this.closed) return;
    setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
      this.connect();
    }, this.reconnectDelay);
  }
}
