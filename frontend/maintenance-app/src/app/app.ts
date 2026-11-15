import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private http = inject(HttpClient);
  private readonly api = {
    inventory: 'http://localhost:8001',
    maintenance: 'http://localhost:8005',
    relocation: 'http://localhost:8006',
    acquisitions: 'http://localhost:8007',
  };

  vehicles: any[] = [];
  orders: any[] = [];
  relocations: any[] = [];

  acq = { vehicle_type: 'SCOOTER', model: '', zone_id: 'ZONA-1', quantity: 1, unit_cost: 350 };
  mnt = { vehicle_id: '', order_type: 'RECHARGE', reason: '' };

  ngOnInit(): void {
    this.loadAll();
  }

  loadAll(): void {
    this.http.get<any[]>(`${this.api.inventory}/vehicles`).subscribe((d) => (this.vehicles = d));
    this.http.get<any[]>(`${this.api.maintenance}/maintenance-orders`).subscribe((d) => (this.orders = d));
    this.http.get<any[]>(`${this.api.relocation}/relocation-orders`).subscribe((d) => (this.relocations = d));
  }

  get openMaintenanceCount(): number {
    return this.orders.filter((o) => o.status !== 'COMPLETED').length;
  }

  get pendingRelocationCount(): number {
    return this.relocations.filter((r) => r.status !== 'COMPLETED').length;
  }

  createAcquisition(): void {
    this.http.post(`${this.api.acquisitions}/acquisitions`, this.acq).subscribe(() => {
      this.acq.model = '';
      this.loadAll();
    });
  }

  createMaintenance(): void {
    this.http.post(`${this.api.maintenance}/maintenance-orders`, this.mnt).subscribe(() => {
      this.mnt = { vehicle_id: '', order_type: 'RECHARGE', reason: '' };
      this.loadAll();
    });
  }

  completeMaintenance(id: string): void {
    this.http.patch(`${this.api.maintenance}/maintenance-orders/${id}/complete`, {}).subscribe(() => this.loadAll());
  }

  completeRelocation(id: string): void {
    this.http
      .patch(`${this.api.relocation}/relocation-orders/${id}/status`, { status: 'COMPLETED' })
      .subscribe(() => this.loadAll());
  }
}
