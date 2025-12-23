import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Gov.co Header Bar */}
      <div className="w-full bg-[#0943b5] py-[5px]">
        <div className="w-full max-w-[1280px] mx-auto px-4">
          <a href="https://www.gov.co/" target="_blank" rel="noopener noreferrer">
            <img
              src="https://www.dnp.gov.co/assets/logo_govco.svg"
              alt="Logo Gov.co"
              className="h-[27px] min-h-[27px] min-w-[135px]"
            />
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header Section */}
        <header className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Módulo de Población
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Observatorio del Sistema de Ciudades - DNP Colombia
          </p>
          <p className="text-md text-gray-500">
            Análisis demográfico con datos DANE 2018-2070
          </p>
        </header>

        {/* Main Modules Grid */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Módulos de Análisis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Mapa */}
            <Link
              href="/mapa"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">🗺️</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Mapa Interactivo
              </h2>
              <p className="text-gray-600">
                Visualiza la distribución territorial de variables demográficas en mapas categorizados
              </p>
            </Link>

            {/* Pirámide */}
            <Link
              href="/piramide"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">📊</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Pirámide Poblacional
              </h2>
              <p className="text-gray-600">
                Estructura por edad y sexo con 3 modos de agrupación y visualización porcentual
              </p>
              <div className="mt-3 flex gap-2 flex-wrap">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Años simples</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Quinquenal</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Grupos</span>
              </div>
            </Link>

            {/* Serie de Tiempo */}
            <Link
              href="/serie-tiempo"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">📈</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Serie de Tiempo
              </h2>
              <p className="text-gray-600">
                Evolución histórica de la población con tasas de crecimiento y cambio absoluto
              </p>
              <div className="mt-3 flex gap-2 flex-wrap">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Crecimiento</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Delta</span>
              </div>
            </Link>

            {/* Indicadores DANE */}
            <Link
              href="/indicadores"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">📈</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Indicadores DANE
              </h2>
              <p className="text-gray-600">
                Explora indicadores de fecundidad demográfica por región y año (2018-2070)
              </p>
              <div className="mt-3 flex gap-2 flex-wrap">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">TGF</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Tasas por edad</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">23 Regiones</span>
              </div>
            </Link>

            {/* Bono Demográfico */}
            <Link
              href="/bono-demografico"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">📉</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Bono Demográfico
              </h2>
              <p className="text-gray-600">
                Analiza el dividendo demográfico y la transición poblacional por territorios
              </p>
            </Link>

            {/* Chat IA */}
            <Link
              href="/chat"
              className="group p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-xl transition-all duration-300"
            >
              <div className="text-4xl mb-4">🤖</div>
              <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                Chat IA
              </h2>
              <p className="text-gray-600">
                Consulta datos poblacionales en lenguaje natural con asistente inteligente
              </p>
              <div className="mt-3 flex gap-2 flex-wrap">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Claude AI</span>
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">SQL Natural</span>
              </div>
            </Link>

          </div>
        </div>

        {/* Resources Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recursos y Herramientas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Glosario */}
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">📖</div>
                <h3 className="text-xl font-semibold text-gray-900">Glosario Demográfico</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Accede a 30+ términos demográficos con definiciones detalladas, ejemplos y conceptos relacionados
              </p>
              <p className="text-sm text-gray-500">
                Disponible desde el botón "Glosario" en la barra de navegación
              </p>
            </div>

            {/* API Documentation */}
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">🔌</div>
                <h3 className="text-xl font-semibold text-gray-900">API REST</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Acceso programático a datos poblacionales y indicadores DANE
              </p>
              <Link href="/api/docs" className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                Ver documentación →
              </Link>
            </div>
          </div>
        </div>

        {/* Data Sources */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* DANE Source */}
          <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
            <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-gray-900">
              <span>📊</span> Fuente de Datos Principal
            </h3>
            <p className="mb-2 font-medium text-gray-800">
              DANE - Departamento Administrativo Nacional de Estadística
            </p>
            <p className="text-gray-600 text-sm mb-3">
              Proyecciones de Población 2018-2070 (actualizado Julio 2025)
            </p>
            <div className="flex gap-2 flex-wrap">
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Nivel Departamental</span>
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Nivel Municipal</span>
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">23 Regiones</span>
            </div>
          </div>

          {/* Coverage Stats */}
          <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
            <h3 className="text-lg font-bold mb-3 text-gray-900">Cobertura de Datos</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-3xl font-bold text-blue-600">1,103</p>
                <p className="text-sm text-gray-600">Municipios</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">20</p>
                <p className="text-sm text-gray-600">Áreas No Municipalizadas</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">33</p>
                <p className="text-sm text-gray-600">Departamentos</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-blue-600">23</p>
                <p className="text-sm text-gray-600">Regiones DANE</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="text-center text-sm text-gray-500">
          <p>Observatorio del Sistema de Ciudades - Departamento Nacional de Planeación</p>
          <p className="mt-1">© 2025 DNP Colombia</p>
        </div>
      </div>
    </main>
  )
}
