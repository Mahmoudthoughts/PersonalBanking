export interface Tag {
  id: number;
  name: string;
  parent_id?: number | null;
  children?: Tag[];
}
