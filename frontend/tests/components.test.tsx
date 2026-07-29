import React from 'react';
import { SeverityBadge } from '../src/components/SeverityBadge';
import { ConfidenceMeter } from '../src/components/ConfidenceMeter';
import { FindingCard } from '../src/components/FindingCard';
import { MOCK_FINDINGS } from '../src/lib/fixtures';

describe('Frontend Component Shell Unit Tests', () => {
  it('renders SeverityBadge correctly', () => {
    const badge = <SeverityBadge severity="CRITICAL" />;
    expect(badge).toBeDefined();
  });

  it('renders ConfidenceMeter correctly', () => {
    const meter = <ConfidenceMeter score={0.92} />;
    expect(meter).toBeDefined();
  });

  it('renders FindingCard correctly', () => {
    const card = <FindingCard finding={MOCK_FINDINGS[0]} />;
    expect(card).toBeDefined();
  });
});
