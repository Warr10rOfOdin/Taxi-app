import { useState, useEffect } from 'react';
import { Building2, Users, Landmark, FileStack, Plus, Edit, Trash2 } from 'lucide-react';
import { api } from '../api/client';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('company');
  const [companies, setCompanies] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const tabs = [
    { id: 'company', name: 'Selskapsinfo', icon: Building2 },
    { id: 'drivers', name: 'Sjåfører', icon: Users },
    { id: 'banks', name: 'Bankkontoer', icon: Landmark },
    { id: 'templates', name: 'Maler', icon: FileStack },
  ];

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'company') {
        const { data } = await api.getCompanies();
        setCompanies(data);
      } else if (activeTab === 'drivers') {
        const { data } = await api.getDrivers();
        setDrivers(data);
      } else if (activeTab === 'banks') {
        const { data } = await api.getBankAccounts();
        setBankAccounts(data);
      } else if (activeTab === 'templates') {
        const { data } = await api.getTemplates();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, type) => {
    if (!confirm('Er du sikker på at du vil slette dette?')) return;

    try {
      if (type === 'company') await api.deleteCompany(id);
      else if (type === 'driver') await api.deleteDriver(id);
      else if (type === 'bank') await api.deleteBankAccount(id);
      else if (type === 'template') await api.deleteTemplate(id);

      loadData();
    } catch (error) {
      console.error('Error deleting:', error);
      alert('Feil ved sletting');
    }
  };

  const openModal = (item = null) => {
    setEditingItem(item);
    setShowModal(true);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="card">
        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="flex gap-4">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div>
          {/* Company Tab */}
          {activeTab === 'company' && (
            <CompanyTab
              companies={companies}
              onAdd={() => openModal()}
              onEdit={(item) => openModal(item)}
              onDelete={(id) => handleDelete(id, 'company')}
              loading={loading}
            />
          )}

          {/* Drivers Tab */}
          {activeTab === 'drivers' && (
            <DriversTab
              drivers={drivers}
              onAdd={() => openModal()}
              onEdit={(item) => openModal(item)}
              onDelete={(id) => handleDelete(id, 'driver')}
              loading={loading}
            />
          )}

          {/* Banks Tab */}
          {activeTab === 'banks' && (
            <BanksTab
              accounts={bankAccounts}
              onAdd={() => openModal()}
              onEdit={(item) => openModal(item)}
              onDelete={(id) => handleDelete(id, 'bank')}
              loading={loading}
            />
          )}

          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <TemplatesTab
              templates={templates}
              onAdd={() => openModal()}
              onEdit={(item) => openModal(item)}
              onDelete={(id) => handleDelete(id, 'template')}
              loading={loading}
            />
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <Modal
          type={activeTab}
          item={editingItem}
          onClose={() => {
            setShowModal(false);
            setEditingItem(null);
          }}
          onSave={() => {
            setShowModal(false);
            setEditingItem(null);
            loadData();
          }}
        />
      )}
    </div>
  );
}

// Company Tab Component
function CompanyTab({ companies, onAdd, onEdit, onDelete, loading }) {
  if (loading) return <div>Laster...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Selskapsinfo</h3>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Legg til selskap
        </button>
      </div>

      {companies.length === 0 ? (
        <p className="text-gray-500">Ingen selskaper registrert</p>
      ) : (
        <div className="space-y-4">
          {companies.map((company) => (
            <div key={company.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-lg">{company.name}</h4>
                  {company.org_number && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">Org.nr: {company.org_number}</p>
                  )}
                  {company.address && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">{company.address}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => onEdit(company)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button onClick={() => onDelete(company.id)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Drivers Tab Component
function DriversTab({ drivers, onAdd, onEdit, onDelete, loading }) {
  if (loading) return <div>Laster...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Sjåfører</h3>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Legg til sjåfør
        </button>
      </div>

      {drivers.length === 0 ? (
        <p className="text-gray-500">Ingen sjåfører registrert</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Navn</th>
                <th>Sjåfør-ID</th>
                <th>Provisjon</th>
                <th>Standard</th>
                <th>Handlinger</th>
              </tr>
            </thead>
            <tbody>
              {drivers.map((driver) => (
                <tr key={driver.id}>
                  <td>{driver.name}</td>
                  <td>{driver.driver_id}</td>
                  <td>{driver.commission_percentage}%</td>
                  <td>{driver.is_default ? '✓' : ''}</td>
                  <td>
                    <div className="flex gap-2">
                      <button onClick={() => onEdit(driver)} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button onClick={() => onDelete(driver.id)} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// Banks Tab Component
function BanksTab({ accounts, onAdd, onEdit, onDelete, loading }) {
  if (loading) return <div>Laster...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Bankkontoer</h3>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Legg til bankkonto
        </button>
      </div>

      {accounts.length === 0 ? (
        <p className="text-gray-500">Ingen bankkontoer registrert</p>
      ) : (
        <div className="space-y-3">
          {accounts.map((account) => (
            <div key={account.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg flex justify-between items-center">
              <div>
                <p className="font-semibold">{account.account_number}</p>
                {account.account_name && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{account.account_name}</p>
                )}
                {account.is_default && (
                  <span className="text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-2 py-1 rounded">
                    Standard
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <button onClick={() => onEdit(account)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                  <Edit className="h-4 w-4" />
                </button>
                <button onClick={() => onDelete(account.id)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Templates Tab Component
function TemplatesTab({ templates, onAdd, onEdit, onDelete, loading }) {
  if (loading) return <div>Laster...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Maler</h3>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Legg til mal
        </button>
      </div>

      {templates.length === 0 ? (
        <p className="text-gray-500">Ingen maler registrert</p>
      ) : (
        <div className="space-y-3">
          {templates.map((template) => (
            <div key={template.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold">{template.name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{template.template_type}</p>
                  <p className="text-xs text-gray-500 mt-1">{template.columns.length} kolonner</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => onEdit(template)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button onClick={() => onDelete(template.id)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Modal Component (simplified - would need full form implementations)
function Modal({ type, item, onClose, onSave }) {
  const [formData, setFormData] = useState(item || {});

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (type === 'company') {
        if (item) {
          await api.updateCompany(item.id, formData);
        } else {
          await api.createCompany(formData);
        }
      } else if (type === 'drivers') {
        if (item) {
          await api.updateDriver(item.id, formData);
        } else {
          await api.createDriver(formData);
        }
      } else if (type === 'banks') {
        if (item) {
          await api.updateBankAccount(item.id, formData);
        } else {
          await api.createBankAccount(formData);
        }
      } else if (type === 'templates') {
        if (item) {
          await api.updateTemplate(item.id, formData);
        } else {
          await api.createTemplate(formData);
        }
      }
      onSave();
    } catch (error) {
      console.error('Error saving:', error);
      alert('Feil ved lagring');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 className="text-xl font-bold mb-4">
          {item ? 'Rediger' : 'Legg til'} {type === 'company' ? 'selskap' : type === 'drivers' ? 'sjåfør' : type === 'banks' ? 'bankkonto' : 'mal'}
        </h3>
        <form onSubmit={handleSubmit}>
          {/* Form fields would go here based on type */}
          <p className="text-sm text-gray-500 mb-4">Skjema implementeres...</p>

          <div className="flex justify-end gap-2 mt-4">
            <button type="button" onClick={onClose} className="btn-secondary">
              Avbryt
            </button>
            <button type="submit" className="btn-primary">
              Lagre
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
