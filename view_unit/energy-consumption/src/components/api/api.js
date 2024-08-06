// api.js

export const fetchServers = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/servers');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      return data; // Retourne les données récupérées depuis le backend
    } catch (error) {
      console.error('Error fetching servers:', error);
      throw error; // Propage l'erreur pour gérer dans le composant qui utilise cette fonction
    }
};


export const fetchVMs = async (serverNames, serverIPs) => {
  try {
      // Construire l'URL avec les paramètres server et ip
      const url = new URL('http://127.0.0.1:5000/vms');

      serverNames.forEach((serverName, index) => {
          url.searchParams.append('server', serverName);
          url.searchParams.append('ip', serverIPs[index]);
      });

      const response = await fetch(url);
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log(data)
      return data; // Retourne les données récupérées depuis le backend
  } catch (error) {
      console.error('Error fetching VMs:', error);
      throw error; // Propage l'erreur pour gérer dans le composant qui utilise cette fonction
  }
};


export const fetchEnergyConsumption = async (selectedVMs, dateRange) => {
  try {
    const response = await fetch('http://127.0.0.1:5000/energy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        vms: selectedVMs,
        dateRange: dateRange
      }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return response;
  } catch (error) {
    console.error('Error fetching energy consumption:', error);
    throw error; // Re-throw the error to be caught by the caller
  }
};
