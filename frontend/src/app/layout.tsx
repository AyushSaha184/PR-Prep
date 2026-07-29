import './globals.css';
import React from 'react';
import { Layout } from '../components/Layout';

export const metadata = {
  title: 'PR Prep — Automated PR Reviewer',
  description: 'Selective automated pull-request reviewer with four specialist AI agents.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
