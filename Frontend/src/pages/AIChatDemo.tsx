import { AIChat } from "../components/AIChat";

export default function AIChatDemo() {
  // Use the farmer ID from our tests
  const farmerId = "6917d631cc91724e7c5d0312";

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🤖 Asistent AI pentru Fermieri
          </h1>
          <p className="text-gray-600">
            Întreabă orice despre ferma ta - comenzi, inventar, culturi,
            task-uri
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Powered by OpenRouter (Gemini 2.5 Flash) + MongoDB
          </p>
        </div>

        <AIChat farmerId={farmerId} />

        {/* Features */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl mb-2">🎤</div>
            <h3 className="font-semibold mb-1">Voice Input</h3>
            <p className="text-sm text-gray-600">
              Vorbește direct cu asistentul
            </p>
          </div>

          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl mb-2">🔊</div>
            <h3 className="font-semibold mb-1">Text-to-Speech</h3>
            <p className="text-sm text-gray-600">Ascultă răspunsurile</p>
          </div>

          <div className="bg-white p-4 rounded-lg shadow text-center">
            <div className="text-2xl mb-2">🧠</div>
            <h3 className="font-semibold mb-1">AI Real</h3>
            <p className="text-sm text-gray-600">Înțelege limbaj natural</p>
          </div>
        </div>

        {/* Example queries */}
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold text-lg mb-3">
            📝 Exemple de întrebări:
          </h3>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>"Ce comenzi am astăzi și cât valorează?"</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>
                "Cât am vândut în ultima lună și care e media per comandă?"
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>
                "Ce task-uri am de făcut astăzi? Arată-mi și pe cele întârziate"
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>"Spune-mi valoarea totală a inventarului meu"</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>"Ce culturi am și când trebuie să le recoltez?"</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600">•</span>
              <span>"Dă-mi un rezumat complet al fermei mele"</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
