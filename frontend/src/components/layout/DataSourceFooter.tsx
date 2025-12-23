import React from 'react';

/**
 * DataSourceFooter - Displays DANE data source attribution
 * Required by stakeholders to show data provenance on all pages
 */
export const DataSourceFooter: React.FC = () => {
  return (
    <footer className="w-full border-t bg-muted/30 py-3 px-4 md:px-6 mt-auto">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-2 text-xs md:text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <span className="font-medium">Fuente:</span>
            <span>DANE - Proyecciones de Población 2018-2050</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="font-medium">Actualizado:</span>
            <span>30 de Julio de 2025</span>
          </div>
          <div className="flex items-center gap-1 text-xs">
            <span>Dirección de Censos y Demografía (DCD)</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default DataSourceFooter;
