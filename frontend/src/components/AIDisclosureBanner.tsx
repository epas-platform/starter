'use client';

import { useState } from 'react';

/**
 * AI Disclosure Banner
 *
 * Stub component for future AI disclosure compliance (EU AI Act, Utah/Colorado laws).
 * When AI features are added, this banner will display:
 * - Which AI features were used in the session
 * - Model information
 * - Acknowledgment mechanism
 */
export function AIDisclosureBanner() {
  const [dismissed, setDismissed] = useState(false);

  // For now, this is a stub - no AI features are active
  const aiFeatures: string[] = [];

  // Don't show if no AI features used or already dismissed
  if (aiFeatures.length === 0 || dismissed) {
    return null;
  }

  return (
    <div
      role="alert"
      className="fixed bottom-0 left-0 right-0 bg-blue-50 dark:bg-blue-900/50 border-t border-blue-200 dark:border-blue-800 p-4"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-blue-600 dark:text-blue-400">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </span>
          <div>
            <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
              AI Disclosure
            </p>
            <p className="text-sm text-blue-600 dark:text-blue-300">
              This session used AI-powered features: {aiFeatures.join(', ')}
            </p>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 underline"
        >
          Acknowledge
        </button>
      </div>
    </div>
  );
}

/**
 * Hook for components to register AI feature usage
 * Placeholder for future implementation
 */
export function useAIDisclosure() {
  const registerAIUsage = (featureName: string, modelUsed?: string) => {
    // Future: Track AI feature usage for disclosure
    console.log(`AI feature used: ${featureName}`, modelUsed);
  };

  return { registerAIUsage };
}
