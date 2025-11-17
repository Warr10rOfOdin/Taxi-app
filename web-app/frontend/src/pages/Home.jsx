import { FileText, DollarSign, Settings, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Home() {
  const features = [
    {
      name: 'Skiftrapport',
      description: 'Last opp og generer skiftrapporter med kontantjusteringer og PDF-eksport',
      icon: FileText,
      path: '/shift-report',
      color: 'bg-blue-500',
    },
    {
      name: 'Lønnsrapport',
      description: 'Beregn lønn basert på provisjon og generer detaljerte lønnsrapporter',
      icon: DollarSign,
      path: '/salary-report',
      color: 'bg-green-500',
    },
    {
      name: 'Innstillinger',
      description: 'Administrer selskapsinfo, sjåfører, bankkontoer og maler',
      icon: Settings,
      path: '/settings',
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="card mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-primary-100 dark:bg-primary-900 rounded-lg">
            <TrendingUp className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              Velkommen til Voss Taxi Rapportmaker
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Administrer skiftrapporter og lønnsberegninger enkelt og effektivt
            </p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.name}
              to={feature.path}
              className="card hover:shadow-lg transition-shadow cursor-pointer group"
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 ${feature.color} rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    {feature.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Start Guide */}
      <div className="card mt-8">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Hurtigstart
        </h2>
        <ol className="space-y-3 text-gray-600 dark:text-gray-400">
          <li className="flex gap-3">
            <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 text-sm font-semibold">
              1
            </span>
            <span>
              Gå til <strong>Innstillinger</strong> og legg til selskapsinfo, sjåfører og bankkontoer
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 text-sm font-semibold">
              2
            </span>
            <span>
              Last opp Excel- eller DAT-filer i <strong>Skiftrapport</strong> for å generere rapporter
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 text-sm font-semibold">
              3
            </span>
            <span>
              Bruk <strong>Lønnsrapport</strong> for å beregne lønn basert på provisjon og eksporter til PDF
            </span>
          </li>
        </ol>
      </div>
    </div>
  );
}
