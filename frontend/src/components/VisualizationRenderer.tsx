'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// Dynamically import Plot to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface Visualization {
  type: 'chart' | 'table' | 'text';
  chart_type?: string;
  data?: any;
  title?: string;
  content?: string;
  columns?: string[];
  total_rows?: number;
}

interface VisualizationRendererProps {
  visualizations: Visualization[];
}

export const VisualizationRenderer: React.FC<VisualizationRendererProps> = ({ visualizations }) => {
  if (!visualizations || visualizations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 mt-4">
      {visualizations.map((viz, index) => (
        <Card key={index}>
          {viz.title && (
            <CardHeader>
              <CardTitle className="text-lg">{viz.title}</CardTitle>
            </CardHeader>
          )}
          <CardContent>
            {viz.type === 'chart' && viz.data && (
              <div className="w-full">
                <Plot
                  data={viz.data.data}
                  layout={{
                    ...viz.data.layout,
                    autosize: true,
                    margin: { l: 50, r: 50, t: 50, b: 50 },
                  }}
                  config={{ responsive: true }}
                  className="w-full"
                  useResizeHandler
                  style={{ width: '100%', height: '400px' }}
                />
              </div>
            )}

            {viz.type === 'table' && viz.data && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      {viz.columns?.map((col) => (
                        <th key={col} className="px-4 py-2 text-left font-medium">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {viz.data.slice(0, 50).map((row: any, rowIndex: number) => (
                      <tr key={rowIndex} className="border-b hover:bg-muted/30">
                        {viz.columns?.map((col) => (
                          <td key={col} className="px-4 py-2">
                            {typeof row[col] === 'number'
                              ? row[col].toLocaleString('es-CO')
                              : row[col]?.toString() || '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {viz.total_rows && viz.total_rows > 50 && (
                  <p className="mt-2 text-sm text-muted-foreground">
                    Mostrando primeras 50 filas de {viz.total_rows.toLocaleString('es-CO')} totales
                  </p>
                )}
              </div>
            )}

            {viz.type === 'text' && viz.content && (
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <div dangerouslySetInnerHTML={{ __html: viz.content.replace(/\n/g, '<br />') }} />
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
