import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { WorkspaceService } from '../../../services/workspace.service';
import { Workspace } from '../../../models/workspace';
import { WorkspaceFormComponent } from '../workspace-form/workspace-form';
import { DefaultPageMeta, PageMeta } from 'app/models/shared';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-workspace-list',
  standalone: true,
  imports: [
    CommonModule, 
    MatTableModule, 
    MatButtonModule, 
    MatIconModule, 
    MatCardModule, 
    MatDialogModule,
    MatPaginatorModule
  ],
  templateUrl: './workspace-list.html',
  styleUrls: ['./workspace-list.css']
})
export class WorkspaceListComponent implements OnInit {
  workspaceDC: string[] = ['name', 'apikey', 'instance_uid', 'actions'];
  workspaceDS: MatTableDataSource<Workspace>;
  workspacePA: PageMeta;

  constructor(
    private workspaceService: WorkspaceService,
    private dialog: MatDialog
  ) {
    this.workspaceDS = new MatTableDataSource<Workspace>();
    this.workspacePA = new DefaultPageMeta();
  }

  ngOnInit() {
    this.updateGridTable();
  }

  updateGridTable() {
    this.workspaceService.get(this.workspacePA).subscribe(res => {
      if (res.metadata) {
        this.workspacePA.total_elements = res.metadata.total_elements;
        this.workspaceDS.data = res.data;
      } else {
        this.workspaceDS.data = [];
        this.workspacePA.total_elements = 0;
      }
    });
  }

  nextPage(event: PageEvent) {
    this.workspacePA.page = event.pageIndex + 1;
    this.workspacePA.per_page = event.pageSize;
    this.updateGridTable();
  }

  openForm(workspace?: Workspace) {
    const dialogRef = this.dialog.open(WorkspaceFormComponent, {
      data: workspace || null,
      panelClass: 'custom-dialog-container',
      width: '500px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (workspace?._id) {
          this.workspaceService.update(workspace._id, result).subscribe(() => this.updateGridTable());
        } else {
          this.workspaceService.save(result).subscribe(() => this.updateGridTable());
        }
      }
    });
  }

  onRemove(id: number) {
    if (confirm('Are you sure?')) {
      this.workspaceService.removeById(id).subscribe(() => this.updateGridTable());
    }
  }
}

