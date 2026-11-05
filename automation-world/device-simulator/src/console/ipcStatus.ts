/** 桌面bridge状态与业务操作结果分开；业务校验拒绝不冒充IPC故障。 */
export function ipcStatusKey(available: boolean, bootstrapped: boolean, error: string | null): string {
    if (!available) return 'common.local.desktopPreview';
    if (error === 'ipc_transport_unknown' || error === 'desktop_unavailable') return 'common.local.bootstrapFailed';
    if (bootstrapped) return 'simulator.ipcReady';
    return error ? 'common.local.bootstrapFailed' : 'common.local.loading';
}
