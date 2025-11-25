import { describe, it, expect } from 'vitest';
import { Agent } from '../src/agent/Agent.js';
import { AgentRouter } from '../src/router/AgentRouter.js';

describe('Agent', () => {
  it('registers reasoners and skills directly', () => {
    const agent = new Agent({ nodeId: 'test-agent', devMode: true });
    agent.reasoner('hello', async () => ({ ok: true }));
    agent.skill('format', () => ({ upper: 'X' }));

    expect(agent.reasoners.all().map((r) => r.name)).toContain('hello');
    expect(agent.skills.all().map((s) => s.name)).toContain('format');
  });

  it('includes routers with prefixes', () => {
    const router = new AgentRouter({ prefix: 'simulation' });
    router.reasoner('run', async () => ({}));
    router.skill('format', () => ({}));

    const agent = new Agent({ nodeId: 'test-agent', devMode: true });
    agent.includeRouter(router);

    expect(agent.reasoners.all().map((r) => r.name)).toContain('simulation/run');
    expect(agent.skills.all().map((s) => s.name)).toContain('simulation/format');
  });
});
