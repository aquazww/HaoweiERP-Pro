const getPermissions = () => {
  const stored = localStorage.getItem('permissions')
  if (stored) {
    return JSON.parse(stored)
  }
  return {}
}

const getUsername = () => {
  return localStorage.getItem('username') || ''
}

export const hasPermission = (module, action = 'view') => {
  if (getUsername() === 'admin') {
    return true
  }
  const permissions = getPermissions()
  if (!permissions || !permissions[module]) {
    return false
  }
  return permissions[module][action] === true
}

export const hasAnyPermission = (module) => {
  if (getUsername() === 'admin') {
    return true
  }
  const permissions = getPermissions()
  if (!permissions || !permissions[module]) {
    return false
  }
  const modulePerms = permissions[module]
  return Object.values(modulePerms).some(v => v === true)
}

export const canView = (module) => hasPermission(module, 'view')
export const canAdd = (module) => hasPermission(module, 'add')
export const canEdit = (module) => hasPermission(module, 'edit')
export const canDelete = (module) => hasPermission(module, 'delete')
