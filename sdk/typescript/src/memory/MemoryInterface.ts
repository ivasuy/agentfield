import type { MemoryScope } from '../types/agent.js';
import type { MemoryClient } from './MemoryClient.js';
import type { MemoryEventClient } from './MemoryEventClient.js';

export interface MemoryChangeEvent {
  key: string;
  data: any;
  scope: MemoryScope;
  scopeId: string;
  timestamp: string | Date;
  agentId: string;
}

export type MemoryWatchHandler = (event: MemoryChangeEvent) => Promise<void> | void;

export class MemoryInterface {
  private readonly client: MemoryClient;
  private readonly eventClient?: MemoryEventClient;
  private readonly defaultScope: MemoryScope;
  private readonly defaultScopeId?: string;

  constructor(params: {
    client: MemoryClient;
    eventClient?: MemoryEventClient;
    defaultScope?: MemoryScope;
    defaultScopeId?: string;
  }) {
    this.client = params.client;
    this.eventClient = params.eventClient;
    this.defaultScope = params.defaultScope ?? 'workflow';
    this.defaultScopeId = params.defaultScopeId;
  }

  async set(key: string, data: any, scope: MemoryScope = this.defaultScope, scopeId = this.defaultScopeId) {
    await this.client.set(key, data, scope, scopeId);
  }

  get<T = any>(key: string, scope: MemoryScope = this.defaultScope, scopeId = this.defaultScopeId) {
    return this.client.get<T>(key, scope, scopeId);
  }

  async setVector(key: string, vector: number[], metadata?: any, scope: MemoryScope = this.defaultScope, scopeId = this.defaultScopeId) {
    await this.client.setVector(key, vector, metadata, scope, scopeId);
  }

  searchVector(query: number[] | string, options?: { limit?: number }) {
    return this.client.searchVector(query, options);
  }

  onEvent(handler: MemoryWatchHandler) {
    this.eventClient?.onEvent(handler);
  }
}
