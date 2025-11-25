import { generateText, streamText, type StreamTextResult } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';
import type { ZodSchema } from 'zod';
import type { AIConfig } from '../types/agent.js';

export interface AIRequestOptions {
  system?: string;
  schema?: ZodSchema<any>;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  provider?: AIConfig['provider'];
}

export type AIStream = AsyncIterable<string>;

export class AIClient {
  private readonly config: AIConfig;

  constructor(config: AIConfig = {}) {
    this.config = config;
  }

  async generate<T = any>(prompt: string, options: AIRequestOptions = {}): Promise<T | string> {
    const model = this.buildModel(options);
    const response = await generateText({
      model,
      prompt,
      system: options.system,
      temperature: options.temperature ?? this.config.temperature,
      maxTokens: options.maxTokens ?? this.config.maxTokens,
      schema: options.schema
    });

    if (options.schema) {
      return response.object as T;
    }

    return response.text;
  }

  async stream(prompt: string, options: AIRequestOptions = {}): Promise<AIStream> {
    const model = this.buildModel(options);
    const streamResult: StreamTextResult<any, any> = await streamText({
      model,
      prompt,
      system: options.system,
      temperature: options.temperature ?? this.config.temperature,
      maxTokens: options.maxTokens ?? this.config.maxTokens
    });

    return streamResult.textStream;
  }

  private buildModel(options: AIRequestOptions) {
    const provider = options.provider ?? this.config.provider ?? 'openai';
    const modelName = options.model ?? this.config.model ?? 'gpt-4o';

    if (provider === 'anthropic') {
      const anthropic = createAnthropic({
        apiKey: this.config.apiKey,
        baseURL: this.config.baseUrl
      });
      return anthropic(modelName);
    }

    // Default to OpenAI / OpenRouter compatible models
    const openai = createOpenAI({
      apiKey: this.config.apiKey,
      baseURL: this.config.baseUrl
    });
    return openai(modelName);
  }
}
