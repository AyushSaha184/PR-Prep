export interface StreamOptions<T> {
  url: string;
  onMessage: (data: T) => void;
  onError?: (err: Event | Error) => void;
  fallbackIntervalMs?: number;
}

export class EventStreamClient<T> {
  private eventSource: EventSource | null = null;
  private retryCount = 0;
  private maxRetries = 5;
  private fallbackTimer: ReturnType<typeof setInterval> | null = null;

  constructor(private options: StreamOptions<T>) {}

  public connect(): void {
    if (typeof window === 'undefined') return;

    try {
      this.eventSource = new EventSource(this.options.url);

      this.eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as T;
          this.retryCount = 0;
          this.options.onMessage(parsed);
        } catch (e) {
          console.error('Failed to parse SSE payload:', e);
        }
      };

      this.eventSource.onerror = (err) => {
        if (this.options.onError) this.options.onError(err);
        this.eventSource?.close();

        if (this.retryCount < this.maxRetries) {
          const backoff = Math.pow(2, this.retryCount) * 1000;
          this.retryCount++;
          setTimeout(() => this.connect(), backoff);
        } else {
          this.startPollingFallback();
        }
      };
    } catch {
      this.startPollingFallback();
    }
  }

  private startPollingFallback(): void {
    if (this.fallbackTimer) return;
    const interval = this.options.fallbackIntervalMs || 5000;
    this.fallbackTimer = setInterval(async () => {
      try {
        const res = await fetch(this.options.url);
        if (res.ok) {
          const data = await res.json();
          this.options.onMessage(data as T);
        }
      } catch (e) {
        // Silent fallback polling swallow
      }
    }, interval);
  }

  public disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.fallbackTimer) {
      clearInterval(this.fallbackTimer);
      this.fallbackTimer = null;
    }
  }
}
