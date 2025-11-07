import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Módulo de Población
          </h1>
          <p className="text-xl text-gray-600">
            Observatorio del Sistema de Ciudades - DNP Colombia
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            href="/mapa"
            className="p-6 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">Mapa Categorizado</h2>
            <p className="text-gray-600">
              Visualiza la distribución territorial de variables demográficas en mapas interactivos
            </p>
          </Link>

          <Link
            href="/piramide"
            className="p-6 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">Pirámide Poblacional</h2>
            <p className="text-gray-600">
              Explora la estructura poblacional por edad y sexo con visualizaciones dinámicas
            </p>
          </Link>

          <Link
            href="/comparador"
            className="p-6 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">Comparador de Territorios</h2>
            <p className="text-gray-600">
              Compara indicadores demográficos entre diferentes territorios
            </p>
          </Link>

          <Link
            href="/bono-demografico"
            className="p-6 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <h2 className="text-2xl font-semibold mb-2">Bono Demográfico</h2>
            <p className="text-gray-600">
              Analiza el bono demográfico y la transición poblacional
            </p>
          </Link>
        </div>

        <div className="mt-12 p-6 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Fuente de datos</h3>
          <p className="text-gray-700">
            Proyecciones de Población 2018-2050 - DANE (Departamento Administrativo Nacional de Estadística)
          </p>
        </div>
      </div>
    </main>
  )
}
