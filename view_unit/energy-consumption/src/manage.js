// utils/manageServer.js
import { useEffect } from 'react';
import { fetchServers, fetchVMs, fetchEnergyConsumption} from './components/api/api.js'; 

export const useManageServers = (setServers) => {
  useEffect(() => {
    const fetchServersData = async () => {
      try {
        const data = await fetchServers();
        setServers(data);
      } catch (error) {
        console.error('Error fetching servers:', error);
        // Gérer l'erreur selon vos besoins (par exemple, afficher un message d'erreur à l'utilisateur)
      }
    };

    fetchServersData();
  }, [setServers]); // Ajout de setServers dans le tableau de dépendances pour éviter les avertissements de linting
};



export const handleServerSelect = async (selected, servers, setSelectedServers, setSelectedVMs) => {
  setSelectedServers(selected);
  try {
    // Récupérer les noms et IPs des serveurs sélectionnés
    const serverNames = selected.map(serverId => servers.find(server => server.id === serverId).name);
    const serverIPs = selected.map(serverId => servers.find(server => server.id === serverId).ip);
    
    // Appeler l'API pour récupérer les VMs des serveurs sélectionnés
    const data = await fetchVMs(serverNames, serverIPs);
    setSelectedVMs(data);
  } catch (error) {
    console.error('Error fetching VMs:', error);
    // Gérer l'erreur selon vos besoins (par exemple, afficher un message d'erreur à l'utilisateur)
  }
};


export const handleSubmit = async (selectedVMs, dateRange, setEnergyData) => {
  // Vérifier si les champs dateRange sont bien définis
  if (!dateRange.start || !dateRange.end) {
    console.error('Date range is not fully defined');
  }

  try {
    const response = await fetchEnergyConsumption(selectedVMs, dateRange);
    if (response.ok) {
      const result = await response.json();
      console.log('Energy consumption data:', result);
      setEnergyData(result); // Met à jour l'état avec les données reçues
    } else {
      console.error('Error fetching energy consumption data');
    }
  } catch (error) {
    console.error('Error submitting data:', error);
  }
};
